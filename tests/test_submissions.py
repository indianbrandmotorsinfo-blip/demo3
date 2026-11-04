from portal.services.assignment_service import AssignmentService
from portal.services.submission_service import SubmissionService
from portal.models.submission import Submission


def test_submission_and_evaluation_lifecycle(app, sample_students, admin_user):
    """
    Submission Lifecycle:
    1. Students form a group
    2. An enrolled student submits GitHub repo URL and Docs URL
    3. Submission status starts as PENDING
    4. Admin reviews and marks as APPROVED with feedback
    5. State is updated and audit trail logged
    """
    with app.app_context():
        # Setup assignment
        assignment = AssignmentService.create_assignment(
            title="Full-Stack Web Portal",
            description="Enterprise Flask application",
            assignment_type="GROUP",
            max_group_size=2,
            max_groups=1,
            created_by_id=admin_user,
        )
        assign_id = assignment.id

        # Enroll students
        AssignmentService.join_assignment_group(assign_id, sample_students[0])
        AssignmentService.join_assignment_group(assign_id, sample_students[1])

        # Student 1 submits project deliverables
        success, msg, submission = SubmissionService.submit_assignment(
            assignment_id=assign_id,
            user_id=sample_students[0],
            repo_url="https://github.com/student-team/fullstack-portal",
            docs_url="https://docs.google.com/document/d/1234567890/edit",
            remarks="Completed with 100% test coverage and Redis caching.",
        )
        assert success is True
        assert submission is not None
        assert submission.status == "PENDING"
        assert submission.repo_url == "https://github.com/student-team/fullstack-portal"

        # Admin evaluates submission
        review_ok, review_msg, updated_sub = SubmissionService.review_submission(
            submission_id=submission.id,
            reviewer_id=admin_user,
            status="APPROVED",
            feedback="Excellent architecture design and clean code separation!",
        )
        assert review_ok is True
        assert updated_sub.status == "APPROVED"
        assert updated_sub.feedback == "Excellent architecture design and clean code separation!"
        assert updated_sub.reviewed_by_id == admin_user
        assert updated_sub.reviewed_at is not None


def test_non_enrolled_student_cannot_submit(app, sample_students, admin_user):
    """Integrity Rule: A student not in a group cannot submit for an assignment."""
    with app.app_context():
        assignment = AssignmentService.create_assignment(
            title="Compiler Design",
            description="Lexer & Parser",
            assignment_type="GROUP",
            max_group_size=2,
            created_by_id=admin_user,
        )

        success, msg, sub = SubmissionService.submit_assignment(
            assignment_id=assignment.id,
            user_id=sample_students[0],
            repo_url="https://github.com/unauthorized/repo",
            docs_url="https://docs.google.com/unauthorized",
        )
        assert success is False
        assert "not a member" in msg.lower()
