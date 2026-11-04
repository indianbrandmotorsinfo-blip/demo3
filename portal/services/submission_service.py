import logging
from datetime import datetime, timezone
from portal.extensions import db
from portal.models.submission import Submission
from portal.models.group import Group, GroupMember
from portal.models.assignment import Assignment
from portal.models.audit_log import AuditLog
from portal.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class SubmissionBusinessError(Exception):
    pass


class SubmissionService:
    """Handles assignment submission lifecycle and administrative reviews."""

    @classmethod
    def submit_assignment(
        cls,
        user,
        assignment_id: int,
        repo_url: str,
        docs_url: str,
        remarks: str = None,
    ) -> Submission:
        """
        Records a project submission for the student's group.
        """
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            raise SubmissionBusinessError("Assignment not found.")

        # Find student's group membership
        membership = (
            db.session.query(GroupMember)
            .filter_by(assignment_id=assignment_id, user_id=user.id)
            .first()
        )
        if not membership:
            raise SubmissionBusinessError("You must be an enrolled team member of this assignment to submit deliverables.")

        group = membership.group

        # Check if submission exists
        existing_sub = group.latest_submission
        if existing_sub:
            # Update existing submission
            existing_sub.repo_url = repo_url.strip()
            existing_sub.docs_url = docs_url.strip()
            existing_sub.remarks = remarks.strip() if remarks else None
            existing_sub.status = Submission.STATUS_PENDING
            existing_sub.submitted_by_id = user.id
            existing_sub.submitted_at = datetime.now(timezone.utc)
            existing_sub.feedback = None  # Reset previous rejection feedback
            sub = existing_sub
        else:
            sub = Submission(
                assignment_id=assignment.id,
                group_id=group.id,
                submitted_by_id=user.id,
                repo_url=repo_url.strip(),
                docs_url=docs_url.strip(),
                remarks=remarks.strip() if remarks else None,
                status=Submission.STATUS_PENDING,
            )
            db.session.add(sub)

        group.status = Group.STATUS_SUBMITTED
        AuditLog.log(
            action="ASSIGNMENT_SUBMITTED",
            entity_type="submission",
            entity_id=assignment.id,
            details=f"{user.full_name} submitted deliverables for group '{group.name}'.",
            user_id=user.id,
        )

        db.session.commit()
        CacheService.invalidate_submission_caches()
        CacheService.invalidate_all_assignment_caches(assignment.id)
        return sub

    @classmethod
    def review_submission(
        cls,
        admin_user,
        submission_id: int,
        decision: str,
        feedback: str = None,
    ) -> Submission:
        """
        Records instructor approval or rejection with feedback.
        """
        submission = db.session.get(Submission, submission_id)
        if not submission:
            raise SubmissionBusinessError("Submission not found.")

        if decision not in [Submission.STATUS_APPROVED, Submission.STATUS_REJECTED]:
            raise SubmissionBusinessError("Invalid review decision.")

        submission.status = decision
        submission.feedback = feedback.strip() if feedback else None
        submission.reviewed_by_id = admin_user.id
        submission.reviewed_at = datetime.now(timezone.utc)

        if submission.group:
            submission.group.status = (
                Group.STATUS_APPROVED if decision == Submission.STATUS_APPROVED else Group.STATUS_REJECTED
            )

        AuditLog.log(
            action=f"SUBMISSION_{decision}",
            entity_type="submission",
            entity_id=submission.id,
            details=f"Admin {admin_user.full_name} marked submission {decision}. Feedback: {feedback[:80] if feedback else 'None'}",
            user_id=admin_user.id,
        )

        db.session.commit()
        CacheService.invalidate_submission_caches()
        CacheService.invalidate_all_assignment_caches(submission.assignment_id)
        return submission
