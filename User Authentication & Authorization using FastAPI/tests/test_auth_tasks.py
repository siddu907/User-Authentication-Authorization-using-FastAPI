import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database import SessionLocal
from main import app
import models


client = TestClient(app)


def reset_db():
    db = SessionLocal()
    db.query(models.Task).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()


def test_signup_login_and_me():
    reset_db()

    signup_response = client.post(
        "/auth/signup",
        json={
            "full_name": "Alice Johnson",
            "email": "alice@example.com",
            "password": "StrongPass123",
        },
    )

    assert signup_response.status_code == 201
    assert signup_response.json()["email"] == "alice@example.com"

    login_response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "StrongPass123",
        },
    )

    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"


def test_refresh_and_admin_access():
    reset_db()

    signup_response = client.post(
        "/auth/signup",
        json={
            "full_name": "Admin User",
            "email": "admin@example.com",
            "password": "StrongPass123",
        },
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = client.post(
        "/auth/refresh",
        json={"token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200

    admin_response = client.get(
        "/auth/admin",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert admin_response.status_code == 403


def test_tasks_are_scoped_to_the_logged_in_user():
    reset_db()

    user_one = client.post(
        "/auth/signup",
        json={
            "full_name": "Alice Johnson",
            "email": "alice@example.com",
            "password": "StrongPass123",
        },
    )
    user_two = client.post(
        "/auth/signup",
        json={
            "full_name": "Bob Smith",
            "email": "bob@example.com",
            "password": "StrongPass123",
        },
    )

    assert user_one.status_code == 201
    assert user_two.status_code == 201

    alice_login = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "StrongPass123"},
    )
    bob_login = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "StrongPass123"},
    )

    alice_token = alice_login.json()["access_token"]
    bob_token = bob_login.json()["access_token"]

    task_response = client.post(
        "/tasks",
        json={"title": "Write report", "description": "Finish the report", "status": "Pending"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    assert task_response.status_code == 201

    bob_task_list = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    assert bob_task_list.status_code == 200
    assert bob_task_list.json() == []

    unauthorized_access = client.get(
        f"/tasks/{task_response.json()['id']}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    assert unauthorized_access.status_code == 403
