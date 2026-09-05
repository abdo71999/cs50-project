from app import app
from io import BytesIO
import pytest
from html.parser import HTMLParser
from database import create_user, save_analysis, select_analyses
from werkzeug.security import generate_password_hash


class CSRFTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "input" and attributes.get("name") == "csrf_token":
            self.token = attributes.get("value")


def get_csrf_token(client, url):
    response = client.get(url)

    assert response.status_code == 200

    parser = CSRFTokenParser()
    parser.feed(response.get_data(as_text=True))

    assert parser.token is not None, "CSRF token not found in response"

    return parser.token


def post_with_csrf(client, url, data=None, token_url=None, **kwargs):
    """Submit a form with the token rendered by its GET page."""
    token = get_csrf_token(client, token_url or url)
    form_data = dict(data or {})
    form_data["csrf_token"] = token
    return client.post(url, data=form_data, **kwargs)


def test_upload_requires_login(client):
    response = client.get("/upload")

    assert response.status_code == 302
    assert response.location == "/login"


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b'name="password"' in response.data


def test_post_without_csrf_token_is_rejected(client):
    response = client.post(
        "/login",
        data={"user_name": "loginuser", "password": "password"},
    )

    assert response.status_code == 400
    assert b"CSRF token" in response.data


def test_login_success(client):
    with app.app_context():
        user_id = create_user(
            "loginuser",
            generate_password_hash("correct-password"),
        )

    response = post_with_csrf(
        client,
        "/login",
        data={"user_name": "loginuser", "password": "correct-password"},
    )

    assert response.status_code == 302
    assert response.location == "/"

    with client.session_transaction() as test_session:
        assert test_session["user_id"] == user_id


def test_login_rejects_invalid_credentials(client):
    response = post_with_csrf(
        client,
        "/login",
        data={"user_name": "unknown", "password": "wrong-password"},
    )

    assert response.status_code == 400
    assert b"Invalid user name or password" in response.data


def test_logout_clears_session(authenticated_client):
    client = authenticated_client

    response = post_with_csrf(client, "/logout", token_url="/")

    assert response.status_code == 302
    assert response.location == "/"

    with client.session_transaction() as test_session:
        assert "user_id" not in test_session

    protected_response = client.get("/history")
    assert protected_response.status_code == 302
    assert protected_response.location == "/login"


def test_upload_page_loads(authenticated_client):
    client = authenticated_client
    response = client.get("/upload")
    assert response.status_code == 200


# define function that uploades a valid csv to re use it
def upload_valid_csv(client):
    return post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,5\n3,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )


def test_file_upload(authenticated_client):
    client = authenticated_client

    response = upload_valid_csv(client)

    assert response.status_code == 302
    assert response.location == "/select_columns"


def test_invalid_upload(authenticated_client):
    client = authenticated_client

    response = post_with_csrf(client, "/upload")

    assert response.status_code == 400


def test_non_csv_upload(authenticated_client):
    client = authenticated_client

    response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,5\n3,7\n"),
                "test.txt",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_select_columns_requires_upload(authenticated_client):
    client = authenticated_client

    response = client.get("/select_columns")

    assert response.status_code == 400


def test_select_columns_with_valid_csv(authenticated_client):
    client = authenticated_client
    upload_response = upload_valid_csv(client)

    assert upload_response.status_code == 302

    select_response = client.get("/select_columns")

    assert select_response.status_code == 200


def test_full_analyze_workflow(authenticated_client):
    client = authenticated_client
    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    select_response = client.get("/select_columns")
    assert select_response.status_code == 200

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 200


def test_invalid_column_names(authenticated_client):
    client = authenticated_client
    # upload first then check analyze
    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "missing", "y_column": "y"},
        token_url="/select_columns",
    )
    assert response.status_code == 400


def test_same_column_names(authenticated_client):
    client = authenticated_client
    # upload first then check analyze
    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "x"},
        token_url="/select_columns",
    )
    assert response.status_code == 400


def test_analyze_without_upload(authenticated_client):
    client = authenticated_client
    analyze_response = post_with_csrf(client, "/analyze", token_url="/upload")

    assert analyze_response.status_code == 400


def test_analyze_missing_y_column(authenticated_client):
    client = authenticated_client
    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client, "/analyze", data={"x_column": "x"}, token_url="/select_columns"
    )
    assert analyze_response.status_code == 400


def test_analyze_missing_x_column(authenticated_client):
    client = authenticated_client
    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client, "/analyze", data={"y_column": "y"}, token_url="/select_columns"
    )
    assert analyze_response.status_code == 400


def test_analyze_with_missing_values_in_y(authenticated_client):
    client = authenticated_client

    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,\n3,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_missing_values_in_x(authenticated_client):
    client = authenticated_client

    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n,5\n3,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_nonnumeric_x(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\nunknown,5\n3,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_nonnumeric_y(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,unknown\n3,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_too_few_rows(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,5\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_no_x_variation(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n1,5\n1,7\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_analyze_with_no_y_variation(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,3\n3,3\n"),
                "test.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={"x_column": "x", "y_column": "y"},
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 400


def test_upload_without_name(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b"x,y\n1,3\n2,3\n3,3\n"),
                "",
            )
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 400


def test_upload_unreadable(authenticated_client):
    client = authenticated_client
    upload_response = post_with_csrf(
        client,
        "/upload",
        data={
            "dataset": (
                BytesIO(b'x,y\n1,"unterminated\n2,5\n'),
                "broken.csv",
            )
        },
        content_type="multipart/form-data",
    )

    assert upload_response.status_code == 400


def test_history_after_analysis(authenticated_client):
    client = authenticated_client
    upload_valid_csv(client)

    post_with_csrf(
        client,
        "/analyze",
        data={
            "analysis_name": "My first experiment",
            "x_column": "x",
            "y_column": "y",
        },
        token_url="/select_columns",
    )

    response = client.get("/history")

    assert response.status_code == 200
    assert b"My first experiment" in response.data


def test_empty_history(authenticated_client):
    client = authenticated_client
    response = client.get("/history")

    assert response.status_code == 200
    assert b"No saved analyses yet" in response.data


def test_save_analysis(client):
    with app.app_context():
        analysis_id = save_analysis(
            "Test analysis",
            "1",
            "x",
            "y",
            2.0,
            1.0,
            0.0,
            1.0,
        )

        analyses = select_analyses("1")

    assert analysis_id == 1
    assert len(analyses) == 1
    assert analyses[0]["name"] == "Test analysis"


def test_register(client):
    # Test GET request to /register
    response = client.get("/register")
    assert response.status_code == 200
    assert (
        b'name="user_name"' in response.data
    )  # Assuming the register page contains the word "user_name" in the form

    # Test POST request to /register with valid data
    response = post_with_csrf(
        client, "/register", data={"user_name": "newuser", "password": "newpassword"}
    )
    assert response.status_code == 302  # Redirect after successful registration

    # Test after successful registration, the user_id should be set in the session
    with client.session_transaction() as test_session:
        assert "user_id" in test_session

    # Test POST request to /register with invalid username
    response = post_with_csrf(
        client, "/register", data={"user_name": "invalid123", "password": "newpassword"}
    )
    assert response.status_code == 400
    assert b"Please enter valid user name" in response.data

    # Test POST request to /register with empty password
    response = post_with_csrf(
        client, "/register", data={"user_name": "validuser", "password": ""}
    )
    assert response.status_code == 400
    assert b"please enter a password" in response.data


def test_register_duplicate_username(client):
    # First, register a user
    response = post_with_csrf(
        client,
        "/register",
        data={"user_name": "duplicateuser", "password": "password123"},
    )
    assert response.status_code == 302  # Redirect after successful registration

    # Now, try to register the same username again
    response = post_with_csrf(
        client,
        "/register",
        data={"user_name": "duplicateuser", "password": "newpassword"},
    )
    assert response.status_code == 400
    assert b"User name already exists" in response.data


def test_two_users_history(client):
    # Register first user and perform an analysis
    register_response = post_with_csrf(
        client, "/register", data={"user_name": "alice", "password": "password1"}
    )
    assert register_response.status_code == 302

    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={
            "analysis_name": "User 1 Analysis",
            "x_column": "x",
            "y_column": "y",
        },
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 200

    # Logout first user
    logout_response = post_with_csrf(client, "/logout", token_url="/")
    assert logout_response.status_code == 302

    # Register second user and perform an analysis
    register_response = post_with_csrf(
        client, "/register", data={"user_name": "bob", "password": "password2"}
    )
    assert register_response.status_code == 302

    upload_response = upload_valid_csv(client)
    assert upload_response.status_code == 302

    analyze_response = post_with_csrf(
        client,
        "/analyze",
        data={
            "analysis_name": "User 2 Analysis",
            "x_column": "x",
            "y_column": "y",
        },
        token_url="/select_columns",
    )
    assert analyze_response.status_code == 200

    # Check history for second user
    response = client.get("/history")
    assert response.status_code == 200
    assert b"User 2 Analysis" in response.data
    assert b"User 1 Analysis" not in response.data
