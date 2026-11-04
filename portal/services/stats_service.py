import logging
from sqlalchemy import func
from portal.extensions import db
from portal.models.assignment import Assignment
from portal.models.group import Group, GroupMember
from portal.models.submission import Submission
from portal.models.user import User
from portal.services.cache_service import CacheService
logger = logging.getLogger(__name__)

class StatsService:
    """Computes portal metrics and KPIs with automated Redis caching."""

    @classmethod
    def get_admin_dashboard_metrics(cls) -> dict:
        logger.info("Inside get_admin_dashboard_metrics()")
        cached = CacheService.get_dashboard_stats("admin")
        if cached:
            return cached

        total_assignments = Assignment.query.count()
        open_assignments = Assignment.query.filter_by(status=Assignment.STATUS_OPEN).count()
        full_assignments = Assignment.query.filter_by(status=Assignment.STATUS_FULL).count()
        closed_assignments = Assignment.query.filter_by(status=Assignment.STATUS_CLOSED).count()

        total_students = User.query.filter_by(role=User.ROLE_STUDENT).count()
        total_groups = Group.query.count()
        full_groups = Group.query.filter_by(is_full=True).count()

        total_submissions = Submission.query.count()
        pending_submissions = Submission.query.filter_by(status=Submission.STATUS_PENDING).count()
        approved_submissions = Submission.query.filter_by(status=Submission.STATUS_APPROVED).count()
        rejected_submissions = Submission.query.filter_by(status=Submission.STATUS_REJECTED).count()

        # Enrolled distinct students
        enrolled_students_count = (
            db.session.query(func.count(func.distinct(GroupMember.user_id))).scalar() or 0
        )

        metrics = {
            "assignments": {
                "total": total_assignments,
                "open": open_assignments,
                "full": full_assignments,
                "closed": closed_assignments,
            },
            "students": {
                "total": total_students,
                "enrolled": enrolled_students_count,
                "unassigned": max(0, total_students - enrolled_students_count),
            },
            "groups": {
                "total": total_groups,
                "full": full_groups,
                "forming": max(0, total_groups - full_groups),
            },
            "submissions": {
                "total": total_submissions,
                "pending": pending_submissions,
                "approved": approved_submissions,
                "rejected": rejected_submissions,
            },
        }

        CacheService.set_dashboard_stats("admin", metrics, ttl=180)
        return metrics

    @classmethod
    def get_student_dashboard_metrics(cls, user_id: int) -> dict:
        cached = CacheService.get_dashboard_stats("student", user_id=user_id)
        if cached:
            return cached

        # Memberships
        enrolled_memberships = (
            GroupMember.query.filter_by(user_id=user_id).all()
        )
        enrolled_assignment_ids = [m.assignment_id for m in enrolled_memberships]

        my_active_assignments = len(enrolled_assignment_ids)
        open_available_count = (
            Assignment.query.filter(
                Assignment.status == Assignment.STATUS_OPEN,
                ~Assignment.id.in_(enrolled_assignment_ids) if enrolled_assignment_ids else True,
            ).count()
        )

        my_submissions_count = (
            Submission.query.filter_by(submitted_by_id=user_id).count()
        )
        approved_count = (
            Submission.query.filter_by(submitted_by_id=user_id, status=Submission.STATUS_APPROVED).count()
        )

        data = {
            "my_active_assignments": my_active_assignments,
            "open_available_count": open_available_count,
            "my_submissions_count": my_submissions_count,
            "approved_count": approved_count,
        }

        CacheService.set_dashboard_stats("student", data, user_id=user_id, ttl=120)
        return data

    @classmethod
    def get_detailed_statistics(cls) -> dict:
        cached = CacheService.get_admin_statistics()
        if cached:
            return cached

        metrics = cls.get_admin_dashboard_metrics()

        # Assignment type distribution
        group_type_count = Assignment.query.filter_by(assignment_type=Assignment.TYPE_GROUP).count()
        individual_type_count = Assignment.query.filter_by(assignment_type=Assignment.TYPE_INDIVIDUAL).count()

        # Group size distribution
        size_counts = {}
        for size in [1, 2, 3, 4, 5]:
            count = Assignment.query.filter_by(max_group_size=size).count()
            size_counts[str(size)] = count

        stats = {
            **metrics,
            "assignment_types": {
                "group": group_type_count,
                "individual": individual_type_count,
            },
            "group_size_distribution": size_counts,
        }

        CacheService.set_admin_statistics(stats, ttl=300)
        return stats
