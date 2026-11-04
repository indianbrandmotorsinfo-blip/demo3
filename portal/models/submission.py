from datetime import datetime, timezone
from portal.extensions import db


class Submission(db.Model):
    """Assignment submission by an individual or a group."""

    __tablename__ = "submissions"

    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUSES = [STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED]

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    repo_url = db.Column(db.String(500), nullable=False)
    docs_url = db.Column(db.String(500), nullable=False)
    remarks = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(20),
        nullable=False,
        default=STATUS_PENDING,
        index=True,
    )
    feedback = db.Column(db.Text, nullable=True)
    reviewed_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    submitted_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED')", name="ck_submission_status"),
    )

    # Relationships
    assignment = db.relationship("Assignment", back_populates="submissions")
    group = db.relationship("Group", back_populates="submissions")
    submitted_by = db.relationship(
        "User",
        back_populates="submissions_made",
        foreign_keys=[submitted_by_id],
    )
    reviewed_by = db.relationship(
        "User",
        back_populates="submissions_reviewed",
        foreign_keys=[reviewed_by_id],
    )

    @property
    def is_pending(self) -> bool:
        return self.status == self.STATUS_PENDING

    @property
    def is_approved(self) -> bool:
        return self.status == self.STATUS_APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == self.STATUS_REJECTED

    def to_dict(self):
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "assignment_title": self.assignment.title if self.assignment else "",
            "group_id": self.group_id,
            "group_name": self.group.name if self.group else "",
            "submitted_by": self.submitted_by.full_name if self.submitted_by else "Unknown",
            "repo_url": self.repo_url,
            "docs_url": self.docs_url,
            "remarks": self.remarks,
            "status": self.status,
            "feedback": self.feedback,
            "reviewed_by": self.reviewed_by.full_name if self.reviewed_by else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }

    def __repr__(self):
        return f"<Submission id={self.id} assignment_id={self.assignment_id} status={self.status}>"
