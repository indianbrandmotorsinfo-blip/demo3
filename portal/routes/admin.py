from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, asc
from portal.extensions import db
from portal.models.assignment import Assignment
from portal.models.group import Group, GroupMember
from portal.models.submission import Submission
from portal.models.user import User
from portal.models.audit_log import AuditLog
from portal.forms.assignment_forms import AssignmentForm, AssignmentFilterForm
from portal.forms.submission_forms import ReviewSubmissionForm
from portal.services.assignment_service import AssignmentService, AssignmentBusinessError
from portal.services.submission_service import SubmissionService, SubmissionBusinessError
from portal.services.stats_service import StatsService
from portal.services.cache_service import CacheService
from portal.utilities.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    metrics = StatsService.get_admin_dashboard_metrics()
    recent_assignments = (
        Assignment.query.order_by(desc(Assignment.created_at)).limit(5).all()
    )
    pending_submissions = (
        Submission.query.filter_by(status=Submission.STATUS_PENDING)
        .order_by(desc(Submission.submitted_at))
        .limit(5)
        .all()
    )
    recent_logs = (
        AuditLog.query.order_by(desc(AuditLog.created_at)).limit(8).all()
    )

    return render_template(
        "admin/dashboard.html",
        metrics=metrics,
        recent_assignments=recent_assignments,
        pending_submissions=pending_submissions,
        recent_logs=recent_logs,
    )


@admin_bp.route("/assignments")
@login_required
@admin_required
def assignments():
    filter_form = AssignmentFilterForm(request.args, meta={"csrf": False})
    query = Assignment.query

    # Search filter
    search_term = request.args.get("search", "").strip()
    if search_term:
        query = query.filter(
            Assignment.title.ilike(f"%{search_term}%")
            | Assignment.description.ilike(f"%{search_term}%")
        )

    # Status filter
    status_filter = request.args.get("status", "").strip()
    if status_filter:
        query = query.filter(Assignment.status == status_filter)

    # Type filter
    type_filter = request.args.get("assignment_type", "").strip()
    if type_filter:
        query = query.filter(Assignment.assignment_type == type_filter)

    # Sorting
    sort_by = request.args.get("sort_by", "newest")
    if sort_by == "oldest":
        query = query.order_by(asc(Assignment.created_at))
    elif sort_by == "title_asc":
        query = query.order_by(asc(Assignment.title))
    elif sort_by == "title_desc":
        query = query.order_by(desc(Assignment.title))
    elif sort_by == "due_date":
        query = query.order_by(asc(Assignment.due_date))
    else:
        query = query.order_by(desc(Assignment.created_at))

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "admin/assignments/list.html",
        pagination=pagination,
        assignments=pagination.items,
        filter_form=filter_form,
    )


@admin_bp.route("/assignments/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_assignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            assignment_type=form.assignment_type.data,
            max_group_size=form.max_group_size.data,
            max_groups=form.max_groups.data,
            status=form.status.data,
            due_date=form.due_date.data,
            created_by_id=current_user.id,
        )
        db.session.add(assignment)
        db.session.flush()

        # Automatically assign all students for Individual assignments
        if assignment.assignment_type == Assignment.TYPE_INDIVIDUAL:
            students = User.query.filter_by(role=User.ROLE_STUDENT).all()

            for index, student in enumerate(students, start=1):
                group = Group(
                    assignment_id=assignment.id,
                    group_number=index,
                    name=f"{student.full_name}",
                    is_full=True,
                    status=Group.STATUS_FULL,
                )
                db.session.add(group)
                db.session.flush()

                member = GroupMember(
                    assignment_id=assignment.id,
                    group_id=group.id,
                    user_id=student.id,
                )
                db.session.add(member)

        db.session.commit()

        AuditLog.log(
            action="ASSIGNMENT_CREATED",
            entity_type="assignment",
            entity_id=assignment.id,
            details=f"Admin {current_user.full_name} created '{assignment.title}' (Group size: {assignment.max_group_size}).",
            user_id=current_user.id,
        )

        CacheService.invalidate_all_assignment_caches(assignment.id)
        flash(f"Assignment '{assignment.title}' published successfully!", "success")
        return redirect(url_for("admin.assignments"))

    return render_template("admin/assignments/create.html", form=form)


@admin_bp.route("/assignments/<int:assignment_id>")
@login_required
@admin_required
def assignment_detail(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("admin.assignments"))

    groups = assignment.groups.order_by(Group.group_number.asc()).all()
    submissions = assignment.submissions.order_by(desc(Submission.submitted_at)).all()

    return render_template(
        "admin/assignments/detail.html",
        assignment=assignment,
        groups=groups,
        submissions=submissions,
    )


@admin_bp.route("/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("admin.assignments"))

    form = AssignmentForm(obj=assignment)
    if form.validate_on_submit():
        assignment.title = form.title.data.strip()
        assignment.description = form.description.data.strip()
        assignment.assignment_type = form.assignment_type.data
        assignment.max_group_size = form.max_group_size.data
        assignment.max_groups = form.max_groups.data
        assignment.status = form.status.data
        assignment.due_date = form.due_date.data

        # Recalculate group capacities
        for group in assignment.groups.all():
            group.update_full_status()
        assignment.check_and_update_status()

        db.session.commit()
        CacheService.invalidate_all_assignment_caches(assignment.id)

        AuditLog.log(
            action="ASSIGNMENT_EDITED",
            entity_type="assignment",
            entity_id=assignment.id,
            details=f"Admin {current_user.full_name} updated assignment '{assignment.title}'.",
            user_id=current_user.id,
        )
        flash("Assignment updated successfully!", "success")
        return redirect(url_for("admin.assignment_detail", assignment_id=assignment.id))

    return render_template("admin/assignments/edit.html", form=form, assignment=assignment)


@admin_bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("admin.assignments"))

    title = assignment.title
    db.session.delete(assignment)
    db.session.commit()

    AuditLog.log(
        action="ASSIGNMENT_DELETED",
        entity_type="assignment",
        entity_id=assignment_id,
        details=f"Admin {current_user.full_name} deleted assignment '{title}'.",
        user_id=current_user.id,
    )
    CacheService.invalidate_all_assignment_caches(assignment_id)
    flash(f"Assignment '{title}' deleted successfully.", "info")
    return redirect(url_for("admin.assignments"))


@admin_bp.route("/assignments/<int:assignment_id>/close", methods=["POST"])
@login_required
@admin_required
def close_assignment(assignment_id):
    try:
        AssignmentService.close_assignment(current_user, assignment_id)
        flash("Assignment closed. It will no longer accept new student joins.", "warning")
    except AssignmentBusinessError as exc:
        flash(str(exc), "danger")
    return redirect(request.referrer or url_for("admin.assignments"))


@admin_bp.route("/assignments/<int:assignment_id>/reopen", methods=["POST"])
@login_required
@admin_required
def reopen_assignment(assignment_id):
    try:
        AssignmentService.reopen_assignment(current_user, assignment_id)
        flash("Assignment reopened successfully.", "success")
    except AssignmentBusinessError as exc:
        flash(str(exc), "danger")
    return redirect(request.referrer or url_for("admin.assignments"))


@admin_bp.route("/students")
@login_required
@admin_required
def students():
    search = request.args.get("search", "").strip()
    query = User.query.filter_by(role=User.ROLE_STUDENT)
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%")
            | User.email.ilike(f"%{search}%")
            | User.student_id.ilike(f"%{search}%")
        )

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(asc(User.full_name)).paginate(
        page=page, per_page=current_app.config.get("ITEMS_PER_PAGE", 10), error_out=False
    )
    return render_template("admin/students/list.html", pagination=pagination, students=pagination.items, search=search)


@admin_bp.route("/groups")
@login_required
@admin_required
def groups():
    assignment_id = request.args.get("assignment_id", type=int)
    query = Group.query
    if assignment_id:
        query = query.filter_by(assignment_id=assignment_id)

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(desc(Group.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    all_assignments = Assignment.query.order_by(asc(Assignment.title)).all()
    return render_template(
        "admin/groups/list.html",
        pagination=pagination,
        groups=pagination.items,
        all_assignments=all_assignments,
        selected_assignment_id=assignment_id,
    )


@admin_bp.route("/submissions")
@login_required
@admin_required
def submissions():
    status_filter = request.args.get("status", "").strip()
    query = Submission.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(desc(Submission.submitted_at)).paginate(
        page=page, per_page=current_app.config.get("ITEMS_PER_PAGE", 10), error_out=False
    )
    return render_template(
        "admin/submissions/list.html",
        pagination=pagination,
        submissions=pagination.items,
        status_filter=status_filter,
    )


@admin_bp.route("/submissions/<int:submission_id>/review", methods=["GET", "POST"])
@login_required
@admin_required
def review_submission(submission_id):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        flash("Submission not found.", "danger")
        return redirect(url_for("admin.submissions"))

    form = ReviewSubmissionForm(obj=submission)
    if form.validate_on_submit():
        try:
            SubmissionService.review_submission(
                admin_user=current_user,
                submission_id=submission.id,
                decision=form.status.data,
                feedback=form.feedback.data,
            )
            flash(f"Submission recorded as {form.status.data}.", "success")
            return redirect(url_for("admin.submissions"))
        except SubmissionBusinessError as exc:
            flash(str(exc), "danger")

    return render_template("admin/submissions/review.html", submission=submission, form=form)


@admin_bp.route("/statistics")
@login_required
@admin_required
def statistics():
    stats = StatsService.get_detailed_statistics()
    return render_template("admin/statistics.html", stats=stats)
