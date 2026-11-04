from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from portal.extensions import db, login_manager


class User(UserMixin, db.Model):
    """User model supporting Admin and Student roles."""

    __tablename__ = "users"

    ROLE_ADMIN = "admin"
    ROLE_STUDENT = "student"
    ROLES = [ROLE_ADMIN, ROLE_STUDENT]

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=True, index=True)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    bio = db.Column(db.String(500), nullable=True)

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

    # Relationships
    created_assignments = db.relationship(
        "Assignment",
        back_populates="created_by",
        foreign_keys="Assignment.created_by_id",
        lazy="dynamic",
    )
    memberships = db.relationship(
        "GroupMember",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    submissions_made = db.relationship(
        "Submission",
        back_populates="submitted_by",
        foreign_keys="Submission.submitted_by_id",
        lazy="dynamic",
    )
    submissions_reviewed = db.relationship(
        "Submission",
        back_populates="reviewed_by",
        foreign_keys="Submission.reviewed_by_id",
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN

    @property
    def is_student(self) -> bool:
        return self.role == self.ROLE_STUDENT

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "student_id": self.student_id,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
