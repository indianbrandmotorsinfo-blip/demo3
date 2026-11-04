from datetime import datetime, timezone
from portal.extensions import db


class Assignment(db.Model):
    """Assignment model for individual and group projects."""

    __tablename__ = "assignments"

    TYPE_INDIVIDUAL = "INDIVIDUAL"
    TYPE_GROUP = "GROUP"
    TYPES = [TYPE_INDIVIDUAL, TYPE_GROUP]

    STATUS_OPEN = "OPEN"
    STATUS_FULL = "FULL"
    STATUS_CLOSED = "CLOSED"
    STATUSES = [STATUS_OPEN, STATUS_FULL, STATUS_CLOSED]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    assignment_type = db.Column(
        db.String(20), nullable=False, default=TYPE_GROUP, index=True
    )
    max_group_size = db.Column(db.Integer, nullable=False, default=3)
    max_groups = db.Column(db.Integer, nullable=False, default=1)  # Default 1 official group or multiple
    status = db.Column(
        db.String(20), nullable=False, default=STATUS_OPEN, index=True
    )
    due_date = db.Column(db.DateTime(timezone=True), nullable=True)

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.CheckConstraint("max_group_size >= 1 AND max_group_size <= 5", name="ck_assignment_group_size"),
        db.CheckConstraint("assignment_type IN ('INDIVIDUAL', 'GROUP')", name="ck_assignment_type"),
        db.CheckConstraint("status IN ('OPEN', 'FULL', 'CLOSED')", name="ck_assignment_status"),
    )

    # Relationships
    created_by = db.relationship("User", back_populates="created_assignments", foreign_keys=[created_by_id])
    groups = db.relationship(
        "Group",
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    submissions = db.relationship(
        "Submission",
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def is_open(self) -> bool:
        return self.status == self.STATUS_OPEN

    @property
    def is_full(self) -> bool:
        return self.status == self.STATUS_FULL

    @property
    def is_closed(self) -> bool:
        return self.status == self.STATUS_CLOSED

    def get_current_enrolled_count(self) -> int:
        """Returns total number of students enrolled across all groups for this assignment."""
        total = 0
        for group in self.groups.all():
            total += group.members.count()
        return total

    def check_and_update_status(self) -> str:
        """
        Updates assignment status based on group enrollments:
        When required members join the group(s), automatically transitions to FULL.
        """
        if self.status == self.STATUS_CLOSED:
            return self.status

        # If it's a single official group assignment (e.g. Group Size 3):
        groups = self.groups.all()
        if not groups:
            self.status = self.STATUS_OPEN
            return self.status

        all_full = all(g.is_full for g in groups) and len(groups) >= self.max_groups
        if all_full:
            self.status = self.STATUS_FULL
        else:
            self.status = self.STATUS_OPEN
        return self.status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assignment_type": self.assignment_type,
            "max_group_size": self.max_group_size,
            "max_groups": self.max_groups,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by.full_name if self.created_by else "Admin",
            "enrolled_count": self.get_current_enrolled_count(),
        }

    def __repr__(self):
        return f"<Assignment id={self.id} title={self.title} status={self.status}>"
