import pytest
from database import create_user, verify_user
from app import app
from werkzeug.security import generate_password_hash




def test_verify_user(client):
    # Create a user
    with app.app_context():
        username = "testuser"
        password = "testpassword"
        password_hash = generate_password_hash(password)
        
        user_id = create_user(username, password_hash)

        # Verify the user
        assert verify_user(username, password) == user_id
        assert verify_user(username, "wrongpassword") is False
        assert verify_user("nonexistentuser", password) is False
        assert user_id == 1  # Assuming this is the first user created in the test database
        
        
