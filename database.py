import sqlite3
from flask import current_app, g
from werkzeug.security import check_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    init_db_users()
    init_db_analyses()


def init_db_users():
    db = get_db()
    db.executescript("""CREATE TABLE
    IF NOT EXISTS "users" (
        id INTEGER PRIMARY KEY,
        user_name TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );""")


def init_db_analyses():
    db = get_db()
    db.executescript("""CREATE TABLE
    IF NOT EXISTS "analyses" (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL DEFAULT 'Untitled analysis',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        x_column TEXT NOT NULL,
        y_column TEXT NOT NULL,
        slope REAL NOT NULL,
        intercept REAL NOT NULL,
        rmse REAL NOT NULL,
        r_squared REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );""")
    db.commit()


def save_analysis(name, user_id, x_column, y_column, slope, intercept, rmse, r_squared):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO
    analyses (
        name,
        user_id,
        x_column,
        y_column,
        slope,
        intercept,
        rmse,
        r_squared
    )
VALUES
    (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            name,
            user_id,
            x_column,
            y_column,
            slope,
            intercept,
            rmse,
            r_squared,
        ),
    )
    commit_db(db)

    return cursor.lastrowid


def create_user(user_name, password_hash):
    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO users (user_name, password_hash) VALUES (?,?)""",
            (user_name, password_hash),
        )
        commit_db(db)
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None  # Return None if the username already exists


def verify_user(user_name, password):
    db = get_db()
    cursor = db.execute(
        """SELECT * FROM users WHERE user_name = ?""",
        (user_name,),
    )
    user = cursor.fetchone()
    if user is None:
        return False

    user_password_hash = user["password_hash"]

    if check_password_hash(user_password_hash, password):
        return user["id"]
    return False


def select_analyses(user_id):
    db = get_db()
    cursor = db.execute(
        """ SELECT id, name, created_at, x_column, y_column, slope, intercept, rmse, r_squared
                    FROM analyses
                    WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC;""", (user_id,)
    )
    results = cursor.fetchall()
    return results


def commit_db(db):
    return db.commit()


def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
