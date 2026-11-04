import pytest
from portal.services.assignment_service import AssignmentService
from portal.models.assignment import Assignment
from portal.models.group import Group, GroupMember


def test_first_n_students_lock_group_and_assignment(app, sample_students, admin_user):
    """
    Core Domain Rule:
    The first N students that click Join become the official group.
    When capacity is reached, group is full and assignment transitions to FULL.
    """
    with app.app_context():
        # Create assignment with group size = 3
        assignment = AssignmentService.create_assignment(
            title="Distributed Key-Value Store",
            description="Implement Raft consensus algorithm",
            assignment_type="GROUP",
            max_group_size=3,
            max_groups=1,
            created_by_id=admin_user,
        )
        assign_id = assignment.id

        # Student 1 joins
        success1, msg1, member1 = AssignmentService.join_assignment_group(assign_id, sample_students[0])
        assert success1 is True
        a = Assignment.query.get(assign_id)
        assert a.status == "OPEN"
        group = a.groups.first()
        assert group.member_count == 1
        assert group.is_full is False

        # Student 2 joins
        success2, msg2, member2 = AssignmentService.join_assignment_group(assign_id, sample_students[1])
        assert success2 is True
        a = Assignment.query.get(assign_id)
        assert a.status == "OPEN"
        assert group.member_count == 2
        assert group.is_full is False

        # Student 3 joins (Target capacity 3 reached!)
        success3, msg3, member3 = AssignmentService.join_assignment_group(assign_id, sample_students[2])
        assert success3 is True

        # Check automated state transition
        a = Assignment.query.get(assign_id)
        group = a.groups.first()
        assert group.member_count == 3
        assert group.is_full is True
        assert a.status == "FULL"  # Assignment automatically becomes FULL!

        # Student 4 attempts to join FULL assignment -> Must be rejected!
        success4, msg4, member4 = AssignmentService.join_assignment_group(assign_id, sample_students[3])
        assert success4 is False
        assert "capacity has been reached" in msg4 or "full" in msg4.lower()


def test_students_cannot_leave_once_group_is_full(app, sample_students, admin_user):
    """
    Core Domain Rule:
    Once a group reaches its required size, members are locked in and cannot leave.
    """
    with app.app_context():
        assignment = AssignmentService.create_assignment(
            title="Kubernetes Operator",
            description="CRD controller in Go",
            assignment_type="GROUP",
            max_group_size=2,
            max_groups=1,
            created_by_id=admin_user,
        )
        assign_id = assignment.id

        # Student 1 joins
        AssignmentService.join_assignment_group(assign_id, sample_students[0])

        # Before full: Student 1 CAN leave
        leave_ok, leave_msg = AssignmentService.leave_assignment_group(assign_id, sample_students[0])
        assert leave_ok is True

        # Re-join
        AssignmentService.join_assignment_group(assign_id, sample_students[0])
        # Student 2 joins -> Reaches capacity 2 -> LOCKED FULL
        AssignmentService.join_assignment_group(assign_id, sample_students[1])

        a = Assignment.query.get(assign_id)
        assert a.status == "FULL"

        # Now Student 1 tries to leave -> Must be blocked!
        leave_after_full, msg_after_full = AssignmentService.leave_assignment_group(assign_id, sample_students[0])
        assert leave_after_full is False
        assert "locked" in msg_after_full.lower() or "full" in msg_after_full.lower()


def test_duplicate_membership_prevented(app, sample_students, admin_user):
    """
    Integrity Rule:
    A student cannot join an assignment more than once.
    """
    with app.app_context():
        assignment = AssignmentService.create_assignment(
            title="Blockchain Ledger",
            description="PoW consensus",
            assignment_type="GROUP",
            max_group_size=3,
            created_by_id=admin_user,
        )
        assign_id = assignment.id

        # Student 1 joins
        ok1, _, _ = AssignmentService.join_assignment_group(assign_id, sample_students[0])
        assert ok1 is True

        # Student 1 attempts to join again
        ok2, msg2, _ = AssignmentService.join_assignment_group(assign_id, sample_students[0])
        assert ok2 is False
        assert "already enrolled" in msg2.lower()
