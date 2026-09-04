CREATE TABLE
    users (
        id INTEGER PRIMARY KEY,
        user_name TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS "analyses" (
        id INTEGER PRIMARY KEY,
        users_id INTEGER NOT NULL,
        name TEXT NOT NULL DEFAULT 'Untitled analysis',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        x_column TEXT NOT NULL,
        y_column TEXT NOT NULL,
        slope REAL NOT NULL,
        intercept REAL NOT NULL,
        rmse REAL NOT NULL,
        r_squared REAL NOT NULL,
        FOREIGN KEY users_id REFERENCES users (id)
    );

INSERT INTO
    analyses (
        name,
        user_id x_column,
        y_column,
        slope,
        intercept,
        rmse,
        r_squared
    )
VALUES
    (?, ?, ?, ?, ?, ?, ?, ?),
    (
        name,
        user_id,
        x_column,
        y_column,
        slope,
        intercept,
        rmse,
        r_squared,
    );

INSERT INTO users (user_name, password_hash) VALUES (?,?)