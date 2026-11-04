from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from portal.extensions import db
from portal.models.user import User
from portal.models.audit_log import AuditLog


class AuthService:
    """Service handling user credentials, registration, and password recovery tokens."""

    # Password-reset tokens are *stateless*: a signed, time-limited blob that carries the
    # user id plus a fingerprint of the current password hash. Nothing is stored in
    # process memory (which does not survive across serverless instances), and a token
    # stops working as soon as the password changes, so it is effectively single-use.
    _SALT = "password-reset-v1"

    @classmethod
    def _serializer(cls) -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=cls._SALT)

    @staticmethod
    def _fingerprint(user: User) -> str:
        return (user.password_hash or "")[-16:]

    @classmethod
    def register_student(cls, full_name: str, email: str, password: str, student_id: str = None) -> User:
        user = User(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            student_id=student_id.strip() if student_id else None,
            role=User.ROLE_STUDENT,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        AuditLog.log(
            action="USER_REGISTERED",
            entity_type="user",
            entity_id=user.id,
            details=f"New student {user.full_name} ({user.email}) registered.",
            user_id=user.id,
        )
        return user

    @classmethod
    def generate_password_reset_token(cls, user: User) -> str:
        return cls._serializer().dumps({"uid": user.id, "fp": cls._fingerprint(user)})

    @classmethod
    def verify_password_reset_token(cls, token: str) -> User | None:
        max_age = current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600)
        try:
            data = cls._serializer().loads(token, max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None
        user = db.session.get(User, data.get("uid"))
        if not user or data.get("fp") != cls._fingerprint(user):
            return None
        return user

    @classmethod
    def consume_password_reset_token(cls, token: str, new_password: str) -> bool:
        user = cls.verify_password_reset_token(token)
        if not user:
            return False
        user.set_password(new_password)  # changes the fingerprint -> token can't be reused
        db.session.commit()
        return True
