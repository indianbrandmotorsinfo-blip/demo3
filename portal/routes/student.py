from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, asc
from portal.extensions import db
from portal.models.assignment import Assignment
from portal.models.group import Group, GroupMember
from portal.models.submission import Submission
from portal.forms.assignment_forms import AssignmentFilterForm
from portal.forms.submission_forms import SubmissionForm
from portal.services.assignment_service import AssignmentService, AssignmentBusinessError
from portal.services.submission_service import SubmissionService, SubmissionBusinessError
from portal.services.stats_service import StatsService
from portal.utilities.decorators import student_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    metrics = StatsService.get_student_dashboard_metrics(current_user.id)

    # Get student's enrolled groups
    my_memberships = (
        GroupMember.query.filter_by(user_id=current_user.id)
        .order_by(desc(GroupMember.joined_at))
        .all()
    )

    my_groups = [m.group for m in my_memberships]

    # Open assignments that student hasn't joined yet
    enrolled_assignment_ids = [m.assignment_id for m in my_memberships]
    available_assignments = (
        Assignment.query.filter(
            Assignment.status == Assignment.STATUS_OPEN,
            ~Assignment.id.in_(enrolled_assignment_ids) if enrolled_assignment_ids else True,
        )
        .order_by(desc(Assignment.created_at))
        .limit(6)
        .all()
    )

    return render_template(
        "student/dashboard.html",
        metrics=metrics,
        my_groups=my_groups,
        available_assignments=available_assignments,
    )


@student_bp.route("/assignments")
@login_required
@student_required
def assignments():
    filter_form = AssignmentFilterForm(request.args, meta={"csrf": False})
    query = Assignment.query

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(
            Assignment.title.ilike(f"%{search}%")
            | Assignment.description.ilike(f"%{search}%")
        )

    status_filter = request.args.get("status", "").strip()
    if status_filter:
        query = query.filter(Assignment.status == status_filter)

    type_filter = request.args.get("assignment_type", "").strip()
    if type_filter:
        query = query.filter(Assignment.assignment_type == type_filter)

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
    per_page = current_app.config.get("ITEMS_PER_PAGE", 9)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Pre-fetch user's current memberships
    my_memberships = {
        m.assignment_id: m
        for m in GroupMember.query.filter_by(user_id=current_user.id).all()
    }

    return render_template(
        "student/assignments/list.html",
        pagination=pagination,
        assignments=pagination.items,
        my_memberships=my_memberships,
        filter_form=filter_form,
    )


@student_bp.route("/assignments/<int:assignment_id>")
@login_required
@student_required
def assignment_detail(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("student.assignments"))

    my_membership = (
        GroupMember.query.filter_by(assignment_id=assignment.id, user_id=current_user.id).first()
    )
    my_group = my_membership.group if my_membership else None

    # Official groups for this assignment
    all_groups = assignment.groups.order_by(Group.group_number.asc()).all()

    return render_template(
        "student/assignments/detail.html",
        assignment=assignment,
        my_membership=my_membership,
        my_group=my_group,
        all_groups=all_groups,
    )


@student_bp.route("/assignments/<int:assignment_id>/join", methods=["POST"])
@login_required
@student_required
def join_assignment(assignment_id):
    try:
        group, member = AssignmentService.join_assignment(current_user, assignment_id)
        if group.is_full:
            flash(
                f"You joined '{group.name}'. Target group capacity reached ({group.capacity} members)! The assignment is now locked as FULL.",
                "success",
            )
        else:
            flash(
                f"You successfully joined '{group.name}'. Waiting for {group.capacity - group.member_count} more member(s).",
                "success",
            )
    except AssignmentBusinessError as exc:
        flash(str(exc), "danger")
    except Exception as exc:
        flash(f"Unexpected error while joining: {exc}", "danger")

    return redirect(url_for("student.assignment_detail", assignment_id=assignment_id))


@student_bp.route("/assignments/<int:assignment_id>/leave", methods=["POST"])
@login_required
@student_required
def leave_assignment(assignment_id):
    try:
        AssignmentService.leave_assignment(current_user, assignment_id)
        flash("You have left the assignment group.", "info")
    except AssignmentBusinessError as exc:
        flash(str(exc), "danger")
    except Exception as exc:
        flash(f"Error leaving group: {exc}", "danger")

    return redirect(url_for("student.assignment_detail", assignment_id=assignment_id))


@student_bp.route("/assignments/<int:assignment_id>/submit", methods=["GET", "POST"])
@login_required
@student_required
def submit_assignment(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("student.assignments"))

    if assignment.assignment_type == Assignment.TYPE_INDIVIDUAL:
        my_membership = (
            GroupMember.query.filter_by(
                assignment_id=assignment.id,
                user_id=current_user.id,
            ).first()
        )

        if not my_membership:
            flash(
                "Your individual assignment has not been assigned yet.",
                "danger",
            )
            return redirect(
                url_for("student.assignment_detail", assignment_id=assignment.id)
            )

        group = my_membership.group
        existing_sub = group.latest_submission

    else:
        my_membership = (
            GroupMember.query.filter_by(
                assignment_id=assignment.id,
                user_id=current_user.id,
            ).first()
        )

        if not my_membership:
            flash(
                "You must be an enrolled team member of this assignment to submit deliverables.",
                "danger",
            )
            return redirect(
                url_for("student.assignment_detail", assignment_id=assignment.id)
            )

        group = my_membership.group
        existing_sub = group.latest_submission

    form = SubmissionForm(obj=existing_sub)
    if form.validate_on_submit():
        try:
            SubmissionService.submit_assignment(
                user=current_user,
                assignment_id=assignment.id,
                repo_url=form.repo_url.data,
                docs_url=form.docs_url.data,
                remarks=form.remarks.data,
            )
            flash("Deliverables submitted successfully! Your instructor will review them shortly.", "success")
            return redirect(url_for("student.submissions"))
        except SubmissionBusinessError as exc:
            flash(str(exc), "danger")

    return render_template(
        "student/submissions/submit.html",
        assignment=assignment,
        group=group,
        form=form,
        existing_sub=existing_sub,
    )


@student_bp.route("/submissions")
@login_required
@student_required
def submissions():
    my_group_ids = [
        m.group_id
        for m in GroupMember.query.filter_by(user_id=current_user.id).all()
    ]

    query = Submission.query

    if my_group_ids:
        query = query.filter(
            (Submission.submitted_by_id == current_user.id)
            | (Submission.group_id.in_(my_group_ids))
        )
    else:
        query = query.filter(
            Submission.submitted_by_id == current_user.id
        )

    query = query.order_by(desc(Submission.submitted_at))

    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template(
        "student/submissions/list.html",
        submissions=pagination.items,
        pagination=pagination,
    )
