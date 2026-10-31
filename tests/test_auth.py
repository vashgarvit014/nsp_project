from tests.conftest import login


def test_valid_teacher_login(client):
    resp = login(client, "teacher1@test.com")
    assert resp.status_code == 200
    assert b"Teacher Dashboard" in resp.data


def test_valid_student_login(client):
    resp = login(client, "student1@test.com")
    assert resp.status_code == 200
    assert b"Welcome" in resp.data


def test_incorrect_password(client):
    resp = client.post(
        "/login", data={"email": "teacher1@test.com", "password": "wrongpass"}, follow_redirects=True
    )
    assert b"Invalid email or password" in resp.data


def test_logout_clears_session(client):
    login(client, "teacher1@test.com")
    resp = client.get("/logout", follow_redirects=True)
    assert b"logged out" in resp.data
    resp = client.get("/teacher/dashboard", follow_redirects=True)
    assert b"login" in resp.data.lower() or resp.request.path == "/login"
