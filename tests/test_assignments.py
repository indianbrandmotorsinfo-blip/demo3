from portal.models.assignment import Assignment
from portal.services.assignment_service import AssignmentService
from portal.extensions import db


def test_create_assignment_as_admin(client, app, admin_user):
    """Verify administrator can create assignments with valid sizing."""
    # Authenticate as admin
    client.post("/auth/login", data={"email": "admin@test.edu", "password": "Admin@12345"})

    response = client.post(
        "/admin/assignments/create",
        data={
            "title": "Cloud Microservices Assignment",
            "description": "Build an event-driven architecture using Flask and Redis.",
            "assignment_type": "GROUP",
            "max_group_size": 3,
            "status": "OPEN",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Cloud Microservices Assignment" in response.data

    with app.app_context():
        assignment = Assignment.query.filter_by(title="Cloud Microservices Assignment").first()
        assert assignment is not None
        assert assignment.max_group_size == 3
        assert assignment.status == "OPEN"
        assert assignment.groups.count() >= 1


def test_student_forbidden_from_admin_routes(client, sample_students):
    """Verify student account is forbidden (403) from admin endpoints."""
    client.post("/auth/login", data={"email": "student1@test.edu", "password": "Student@12345"})

    response = client.get("/admin/assignments/create")
    assert response.status_code in [403, 302]
    if response.status_code == 302:
        follow = client.get(response.headers["Location"])
        assert b"Access Denied" in follow.data or b"Access denied" in follow.data or follow.status_code == 403


def test_close_and_reopen_assignment(client, app, admin_user):
    """Test manual locking and unlocking of assignments by admin."""
    client.post("/auth/login", data={"email": "admin@test.edu", "password": "Admin@12345"})

    with app.app_context():
        assignment = AssignmentService.create_assignment(
            title="Database Sharding Project",
            description="Horizontal partition strategy",
            assignment_type="GROUP",
            max_group_size=3,
            created_by_id=admin_user,
        )
        assign_id = assignment.id

    # 1. Close Assignment
    close_resp = client.post(f"/admin/assignments/{assign_id}/close", follow_redirects=True)
    assert close_resp.status_code == 200

    with app.app_context():
        a = Assignment.query.get(assign_id)
        assert a.status == "CLOSED"

    # 2. Reopen Assignment
    reopen_resp = client.post(f"/admin/assignments/{assign_id}/reopen", follow_redirects=True)
    assert reopen_resp.status_code == 200

    with app.app_context():
        a = Assignment.query.get(assign_id)
        assert a.status == "OPEN"
