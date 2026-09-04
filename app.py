import os
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
import secrets
from auth import login_required
from pathlib import Path
import numpy as np
from database import (
    close_db,
    save_analysis,
    init_db,
    select_analyses,
    create_user,
    verify_user,
)
from data_processing import (
    load_dataset,
    get_col_names,
    has_missing_values,
    is_numeric_column,
    has_enough_rows,
    has_variation,
    fit_linear_regression,
    calculate_metrics,
    y_table,
)

app = Flask(__name__)

# Keep uploaded data outside the static directory so Flask never serves it directly.
UPLOAD_FOLDER = Path(__file__).parent / "temporary_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Flask uses this environment-provided secret to sign session cookies.
app.config["SECRET_KEY"] = os.environ["PHYSICS_DATA_LAB_SECRET_KEY"]
app.config["DATABASE"] = Path(app.instance_path) / "analyses.sqlite3"
app.teardown_appcontext(close_db)

with app.app_context():
    init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "dataset" not in request.files:
            return "Missing file field", 400

        dataset = request.files["dataset"]

        if not dataset.filename:
            return "No file Selected", 400

        # Check file extension
        if not dataset.filename.lower().endswith(".csv"):
            return "Please upload CSV file", 400

        # save file name as hex
        upload_id = secrets.token_hex(32)
        file_path = UPLOAD_FOLDER / f"{upload_id}.csv"

        try:
            dataset.save(file_path)
        except OSError:
            file_path.unlink(missing_ok=True)
            return "Could not save file", 500

        try:
            load_dataset(file_path)
        except Exception:
            file_path.unlink(missing_ok=True)
            return "Unable to read CSV file", 400

        # Store only the opaque ID in the session; the uploaded data stays server-side.
        session["upload_id"] = upload_id

        return redirect(url_for("select_columns"))

    return render_template("upload.html")


@app.route("/select_columns", methods=["GET"])
@login_required
def select_columns():

    upload_id = session.get("upload_id")

    if not upload_id:
        return "No active upload", 400

    file_path = UPLOAD_FOLDER / f"{upload_id}.csv"

    if not file_path.is_file():
        return "Uploaded file no longer exists", 400

    data_frame = load_dataset(file_path)
    col_names = get_col_names(data_frame)

    return render_template("select_columns.html", col_names=col_names)


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    analysis_name = request.form.get("analysis_name", "").strip()
    if not analysis_name:
        analysis_name = "Untitled analysis"

    if len(analysis_name) > 100:
        return "Analysis name must be 100 characters or fewer", 400

    x_column = request.form.get("x_column")
    y_column = request.form.get("y_column")

    upload_id = session.get("upload_id")

    if not upload_id:
        return "No active upload", 400

    file_path = UPLOAD_FOLDER / f"{upload_id}.csv"

    if not file_path.is_file():
        return "File does not exist", 400

    # Validate submitted names before using them to index the DataFrame.
    data_frame = load_dataset(file_path)
    col_names = get_col_names(data_frame)
    if x_column not in col_names or y_column not in col_names:
        return "Invalid column names", 400

    if x_column == y_column:
        return "Please choose different X and Y columns", 400

    # Regression requires a complete X/Y pair for every observation.
    if has_missing_values(data_frame, x_column):
        return f"{x_column} has empty or null values", 400

    if has_missing_values(data_frame, y_column):
        return f"{y_column} has empty or null values", 400

    # Both axes must contain numbers; booleans are deliberately rejected.
    if not is_numeric_column(data_frame, x_column):
        return f"{x_column} must be numerical values", 400

    if not is_numeric_column(data_frame, y_column):
        return f"{y_column} must be numerical values", 400

    # Fewer than three observations do not provide enough data for this analysis.
    if not has_enough_rows(data_frame):
        return "Your data does not have enough entries", 400

    # Require variation on both axes so the regression and its metrics are informative.
    if not has_variation(data_frame, x_column):
        return f"{x_column} has not enough variation", 400

    if not has_variation(data_frame, y_column):
        return f"{y_column} has not enough variation", 400

    # calculate vars to pass to html
    model = fit_linear_regression(data_frame, x_column, y_column)
    slope = model.coef_[0]
    intercept = model.intercept_
    prediction = model.predict(data_frame[[x_column]])
    r_squared, rmse = calculate_metrics(data_frame[y_column], prediction)
    x_values = data_frame[x_column].tolist()
    actual_values = data_frame[y_column].tolist()
    predicted_values = prediction.tolist()
    user_id = session["user_id"]

    # save to database
    analysis_id = save_analysis(
        analysis_name, user_id, x_column, y_column, slope, intercept, rmse, r_squared
    )

    return render_template(
        "results.html",
        rmse=rmse,
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        analysis_name=analysis_name,
        y_table=y_table(data_frame[y_column], prediction),
        x_values=x_values,
        actual_values=actual_values,
        predicted_values=predicted_values,
    )


@app.route("/history", methods=["GET"])
@login_required
def history():
    user_id = session["user_id"]
    analyses = select_analyses(user_id)
    return render_template("history.html", analyses=analyses)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        # check valid entries
        if not user_name or not user_name.isalpha():
            return "Please enter valid user name", 400

        if not password:
            return "please enter a password", 400

        password_hash = generate_password_hash(password)

        user_id = create_user(user_name, password_hash)

        # check duplicate user name
        if user_id is None:
            return "User name already exists", 400

        # clear session before logging in new user
        session.clear()

        # new session for new user
        session["user_id"] = user_id

        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        # check valid entries
        if not user_name:
            return "Please enter a user name", 400

        if not password:
            return "please enter a password", 400

        # check correct user
        id = verify_user(user_name, password)
        if id is False:
            return "Invalid user name or password", 400

        session.clear()
        session["user_id"] = id

        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))
