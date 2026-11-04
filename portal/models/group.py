from datetime import datetime, timezone
from portal.extensions import db


class Group(db.Model):
    """Group model representing a student team formed for an assignment."""

    __tablename__ = "groups"

    STATUS_FORMING = "FORMING"
    STATUS_FULL = "FULL"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_number = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.String(100), nullable=False)
    is_full = db.Column(db.Boolean, nullable=False, default=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_FORMING, index=True)

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
        db.UniqueConstraint("assignment_id", "group_number", name="uq_assignment_group_number"),
    )

    # Relationships
    assignment = db.relationship("Assignment", back_populates="groups")
    members = db.relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    submissions = db.relationship(
        "Submission",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def member_count(self) -> int:
        return self.members.count()

    @property
    def capacity(self) -> int:
        return self.assignment.max_group_size if self.assignment else 1

    @property
    def has_space(self) -> bool:
        return not self.is_full and self.member_count < self.capacity

    @property
    def latest_submission(self):
        return self.submissions.order_by(db.desc("submitted_at")).first()

    def update_full_status(self) -> bool:
        """Checks if target members count reached, sets is_full=True, updates assignment status."""
        current_count = self.members.count()
        target = self.capacity
        if current_count >= target:
            self.is_full = True
            if self.status == self.STATUS_FORMING:
                self.status = self.STATUS_FULL
        else:
            self.is_full = False
            if self.status == self.STATUS_FULL:
                self.status = self.STATUS_FORMING
        return self.is_full

    def to_dict(self):
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "group_number": self.group_number,
            "name": self.name,
            "is_full": self.is_full,
            "status": self.status,
            "member_count": self.member_count,
            "capacity": self.capacity,
            "members": [m.to_dict() for m in self.members.all()],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Group id={self.id} assignment_id={self.assignment_id} name='{self.name}' full={self.is_full}>"


class GroupMember(db.Model):
    """Membership mapping between a student and a group, scoped to an assignment."""

    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    joined_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # A student CANNOT join multiple groups for the same assignment or join twice!
        db.UniqueConstraint("assignment_id", "user_id", name="uq_student_assignment_membership"),
    )

    # Relationships
    group = db.relationship("Group", back_populates="members")
    student = db.relationship("User", back_populates="memberships")
    assignment = db.relationship("Assignment")

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "user_id": self.user_id,
            "student_name": self.student.full_name if self.student else "",
            "student_email": self.student.email if self.student else "",
            "student_id": self.student.student_id if self.student else "",
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }

    def __repr__(self):
        return f"<GroupMember id={self.id} group_id={self.group_id} user_id={self.user_id}>"
