import logging
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from portal.extensions import db
from portal.models.assignment import Assignment
from portal.models.group import Group, GroupMember
from portal.models.audit_log import AuditLog
from portal.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class AssignmentBusinessError(Exception):
    """Domain exception for business rule violations."""
    pass


class AssignmentService:
    """Core domain logic for assignment lifecycles, group allocation, and member joining."""

    @classmethod
    def join_assignment(cls, user, assignment_id: int) -> tuple[Group, GroupMember]:
        """
        Enrolls student into the assignment's official group.
        Business Rules Enforced:
        1. Assignment must not be CLOSED.
        2. Assignment must not be FULL.
        3. Student cannot join twice or join multiple groups for the same assignment.
        4. First N students that click Join become the official group.
        5. When required members join (reaches max_group_size), group is FULL and Assignment automatically changes to FULL.
        6. Nobody else can join.
        """
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            raise AssignmentBusinessError("Assignment not found.")

        if assignment.status == Assignment.STATUS_CLOSED:
            raise AssignmentBusinessError("This assignment has been closed by the instructor and is not accepting students.")

        if assignment.status == Assignment.STATUS_FULL:
            raise AssignmentBusinessError("This assignment has already reached full capacity. No further enrollments are permitted.")

        # Rule 1 & 2: Check if student already enrolled in any group for this assignment
        existing_membership = (
            db.session.query(GroupMember)
            .filter_by(assignment_id=assignment_id, user_id=user.id)
            .first()
        )
        if existing_membership:
            raise AssignmentBusinessError("You are already a member of an official group for this assignment.")

        # Find or create open group for this assignment
        # For single cohort / target group size:
        if assignment.assignment_type == Assignment.TYPE_INDIVIDUAL:
            raise AssignmentBusinessError(
                "Individual assignments are automatically assigned to all students."
            )

        # Find or create an open group for group assignments
        open_group = (
            assignment.groups.filter(Group.is_full == False)
            .order_by(Group.group_number.asc())
            .first()
        )
        
        if not open_group:
            # Check if assignment reached max groups allowed
            current_groups_count = assignment.groups.count()
            if current_groups_count >= assignment.max_groups:
                assignment.status = Assignment.STATUS_FULL
                db.session.commit()
                CacheService.invalidate_all_assignment_caches(assignment_id)
                raise AssignmentBusinessError("All groups for this assignment are full.")

            group_num = current_groups_count + 1
            group_name = (
                f"Team {group_num} - {assignment.title}"
                if assignment.assignment_type == Assignment.TYPE_GROUP
                else f"Individual: {user.full_name}"
            )
            open_group = Group(
                assignment_id=assignment.id,
                group_number=group_num,
                name=group_name,
                is_full=False,
                status=Group.STATUS_FORMING,
            )
            db.session.add(open_group)
            db.session.flush()

        # Add member to group
        member = GroupMember(
            group_id=open_group.id,
            user_id=user.id,
            assignment_id=assignment.id,
        )
        db.session.add(member)
        db.session.flush()

        # Update group status
        current_members = open_group.members.count()
        target_size = assignment.max_group_size

        if current_members >= target_size:
            open_group.is_full = True
            open_group.status = Group.STATUS_FULL

            # Rule 5: When required members join, assignment automatically becomes FULL
            # If all allowed groups are full:
            assignment.check_and_update_status()

            AuditLog.log(
                action="GROUP_AND_ASSIGNMENT_LOCKED_FULL",
                entity_type="assignment",
                entity_id=assignment.id,
                details=f"Group '{open_group.name}' reached target {target_size} members. Assignment locked as FULL.",
                user_id=user.id,
            )
        else:
            AuditLog.log(
                action="STUDENT_JOINED_GROUP",
                entity_type="group",
                entity_id=open_group.id,
                details=f"{user.full_name} joined {open_group.name} ({current_members}/{target_size} members).",
                user_id=user.id,
            )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise AssignmentBusinessError("Unable to join: You may already be registered or this group just filled up.")

        # Invalidate caches
        CacheService.invalidate_all_assignment_caches(assignment_id)
        return open_group, member

    @classmethod
    def leave_assignment(cls, user, assignment_id: int) -> bool:
        """
        Allows student to leave assignment ONLY before group becomes full.
        Business Rules Enforced:
        1. Students cannot leave after assignment / group becomes FULL.
        2. Cannot leave if assignment has already been closed.
        3. Cannot leave if assignment has already been submitted.
        """
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            raise AssignmentBusinessError("Assignment not found.")

        membership = (
            db.session.query(GroupMember)
            .filter_by(assignment_id=assignment_id, user_id=user.id)
            .first()
        )
        if not membership:
            raise AssignmentBusinessError("You are not currently enrolled in any group for this assignment.")

        group = membership.group

        # Rule 4: Students cannot leave after assignment becomes FULL
        if assignment.status == Assignment.STATUS_FULL or group.is_full:
            raise AssignmentBusinessError(
                "Locked: You cannot leave after the team or assignment has reached FULL capacity."
            )

        if assignment.status == Assignment.STATUS_CLOSED:
            raise AssignmentBusinessError("Cannot leave a closed assignment.")

        if group.status in [Group.STATUS_SUBMITTED, Group.STATUS_APPROVED]:
            raise AssignmentBusinessError("Cannot leave after a submission has been made.")

        # Remove member
        db.session.delete(membership)
        db.session.flush()

        # If group is now empty, delete it; otherwise keep status as forming
        remaining = group.members.count()
        if remaining == 0:
            db.session.delete(group)
        else:
            group.is_full = False
            group.status = Group.STATUS_FORMING

        # Ensure assignment status is OPEN
        if assignment.status != Assignment.STATUS_CLOSED:
            assignment.status = Assignment.STATUS_OPEN

        AuditLog.log(
            action="STUDENT_LEFT_GROUP",
            entity_type="assignment",
            entity_id=assignment.id,
            details=f"{user.full_name} left group {group.name}.",
            user_id=user.id,
        )

        db.session.commit()
        CacheService.invalidate_all_assignment_caches(assignment_id)
        return True

    @classmethod
    def close_assignment(cls, admin_user, assignment_id: int) -> Assignment:
        """Admin closes assignment so no further students can join."""
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            raise AssignmentBusinessError("Assignment not found.")

        assignment.status = Assignment.STATUS_CLOSED
        AuditLog.log(
            action="ASSIGNMENT_CLOSED_BY_ADMIN",
            entity_type="assignment",
            entity_id=assignment.id,
            details=f"Admin {admin_user.full_name} closed assignment '{assignment.title}'.",
            user_id=admin_user.id,
        )

        db.session.commit()
        CacheService.invalidate_all_assignment_caches(assignment_id)
        return assignment

    @classmethod
    def reopen_assignment(cls, admin_user, assignment_id: int) -> Assignment:
        """Admin reopens a closed assignment."""
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            raise AssignmentBusinessError("Assignment not found.")

        assignment.check_and_update_status()
        AuditLog.log(
            action="ASSIGNMENT_REOPENED",
            entity_type="assignment",
            entity_id=assignment.id,
            details=f"Admin {admin_user.full_name} reopened assignment '{assignment.title}'.",
            user_id=admin_user.id,
        )

        db.session.commit()
        CacheService.invalidate_all_assignment_caches(assignment_id)
        return assignment
