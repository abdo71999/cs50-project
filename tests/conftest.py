import pytest
from app import app
from database import create_user, init_db
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    app.config.update(
        TESTING=True,
        DATABASE=tmp_path / "test.sqlite3",
    )
    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client


@pytest.fixture
def authenticated_client(client):
    """A client whose session belongs to a real user in the temporary database."""
    with app.app_context():
        user_id = create_user(
            "testuser",
            generate_password_hash("test-password"),
        )

    with client.session_transaction() as test_session:
        test_session["user_id"] = user_id

    return client


