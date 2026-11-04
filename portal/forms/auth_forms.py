from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from portal.models.user import User


class LoginForm(FlaskForm):
    """User login form."""

    email = StringField(
        "Email Address",
        validators=[DataRequired(message="Email is required."), Email(message="Enter a valid email address.")],
        render_kw={"placeholder": "student@portal.edu", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
        render_kw={"placeholder": "••••••••", "autocomplete": "current-password"},
    )
    remember_me = BooleanField("Remember me for 30 days")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """Student registration form."""

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "Jane Doe", "autocomplete": "name"},
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=255)],
        render_kw={"placeholder": "jane.doe@portal.edu", "autocomplete": "email"},
    )
    student_id = StringField(
        "Student ID / Roll Number",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "CS-2026-042"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
        render_kw={"placeholder": "Minimum 8 characters", "autocomplete": "new-password"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match exactly."),
        ],
        render_kw={"placeholder": "Re-enter password", "autocomplete": "new-password"},
    )
    submit = SubmitField("Create Student Account")

    def validate_email(self, email):
        existing = User.query.filter_by(email=email.data.strip().lower()).first()
        if existing:
            raise ValidationError("An account with this email already exists.")

    def validate_student_id(self, student_id):
        if student_id.data and student_id.data.strip():
            existing = User.query.filter_by(student_id=student_id.data.strip()).first()
            if existing:
                raise ValidationError("This Student ID is already registered.")


class ForgotPasswordForm(FlaskForm):
    """Password recovery request form."""

    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "name@portal.edu"},
    )
    submit = SubmitField("Send Recovery Instructions")


class ResetPasswordForm(FlaskForm):
    """Password reset confirmation form."""

    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "Enter new password"},
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
        render_kw={"placeholder": "Confirm new password"},
    )
    submit = SubmitField("Set New Password")


class ProfileForm(FlaskForm):
    """User profile update form."""

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=100)],
    )
    student_id = StringField(
        "Student ID",
        validators=[Optional(), Length(max=50)],
    )
    bio = TextAreaField(
        "Bio / Notes",
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "Share your tech stack or interests..."},
    )
    current_password = PasswordField(
        "Current Password (leave blank to keep unchanged)",
        validators=[Optional()],
    )
    new_password = PasswordField(
        "New Password",
        validators=[Optional(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Save Changes")
