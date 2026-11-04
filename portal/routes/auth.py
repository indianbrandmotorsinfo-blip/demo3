from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from portal.extensions import db
from portal.models.user import User
from portal.forms.auth_forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ProfileForm,
)
from portal.services.auth_service import AuthService
from portal.utilities.helpers import is_safe_url

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin else "student.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact an administrator.", "danger")
                return render_template("auth/login.html", form=form)

            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}!", "success")

            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            return redirect(url_for("admin.dashboard" if user.is_admin else "student.dashboard"))
        else:
            flash("Invalid email address or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin else "student.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            AuthService.register_student(
                full_name=form.full_name.data,
                email=form.email.data,
                password=form.password.data,
                student_id=form.student_id.data,
            )
            flash("Registration successful! You may now sign in with your credentials.", "success")
            return redirect(url_for("auth.login"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Registration failed: {exc}", "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been securely signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ForgotPasswordForm()
    reset_token = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if current_app.config.get("SHOW_RESET_LINK"):
            # Demo/local mode only: no email provider is configured, so the link is shown on-page.
            if user:
                reset_token = AuthService.generate_password_reset_token(user)
                flash(
                    "Password recovery initiated. In this demo deployment, click the reset link below.",
                    "info",
                )
            else:
                flash("If that email exists in our system, recovery instructions have been prepared.", "info")
        else:
            # Production: never hand a reset token to an unauthenticated visitor.
            flash(
                "If that email exists in our system, recovery instructions have been prepared. "
                "Password reset by email is not enabled on this deployment - please contact an administrator.",
                "info",
            )

    return render_template("auth/forgot_password.html", form=form, reset_token=reset_token)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = AuthService.verify_password_reset_token(token)
    if not user:
        flash("Invalid or expired password reset link. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if AuthService.consume_password_reset_token(token, form.password.data):
            flash("Password updated successfully! Please sign in with your new password.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Failed to reset password. Please retry.", "danger")

    return render_template("auth/reset_password.html", form=form, token=token)


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.student_id = form.student_id.data.strip() if form.student_id.data else None
        current_user.bio = form.bio.data.strip() if form.bio.data else None

        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash("Current password incorrect. Password was not changed.", "danger")
                return render_template("auth/profile.html", form=form)
            current_user.set_password(form.new_password.data)
            flash("Password updated successfully.", "success")

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", form=form)
