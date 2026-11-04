from portal.models.user import User
from portal.extensions import db


def test_user_registration(client, app):
    """Test standard student registration flow."""
    response = client.post(
        "/auth/register",
        data={
            "email": "newstudent@portal.edu",
            "full_name": "Jane Student",
            "student_id": "CS-9999",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="newstudent@portal.edu").first()
        assert user is not None
        assert user.full_name == "Jane Student"
        assert user.role == "student"
        assert user.check_password("Password123!") is True
        assert user.check_password("WrongPassword") is False


def test_duplicate_registration_rejected(client, sample_students):
    """Test that duplicate institutional emails cannot be registered."""
    response = client.post(
        "/auth/register",
        data={
            "email": "student1@test.edu",
            "full_name": "Imposter Student",
            "student_id": "CS-0001",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already registered" in response.data or b"Email already registered" in response.data


def test_login_and_logout(client, admin_user):
    """Test administrative login and session logout."""
    # 1. Login with valid credentials
    response = client.post(
        "/auth/login",
        data={"email": "admin@test.edu", "password": "Admin@12345"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Administrative Dashboard" in response.data

    # 2. Logout
    logout_resp = client.get("/auth/logout", follow_redirects=True)
    assert logout_resp.status_code == 200
    assert b"Sign In" in logout_resp.data


def test_invalid_password_rejected(client, admin_user):
    """Test rejected authentication on incorrect password."""
    response = client.post(
        "/auth/login",
        data={"email": "admin@test.edu", "password": "IncorrectPassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
