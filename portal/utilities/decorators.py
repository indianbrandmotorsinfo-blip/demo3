from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Restricts access exclusively to authenticated administrators."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please sign in with administrative credentials to access this area.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            flash("Access denied: Administrative privileges are required.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Restricts access exclusively to authenticated students."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please sign in as a student to access this portal.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_student:
            flash("This view is designated for student accounts only.", "info")
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
