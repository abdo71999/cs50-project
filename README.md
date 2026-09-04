# Physics Data Lab

Physics Data Lab is a small Flask app I built to make basic linear regression easier to try with your own data.

You can use it to:

- create an account and sign in
- upload a CSV file
- choose two numerical columns to compare
- fit a linear regression model
- view the slope, intercept, RMSE, R², chart, and predictions
- look back at saved analyses

## Run locally

To run the project, you need Python 3 installed. From the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The app also needs a secret key for user sessions. This command creates one for your local session:

```bash
export PHYSICS_DATA_LAB_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
flask --app app run
```

Now open http://127.0.0.1:5000 in your browser.

The app creates its SQLite database in the local `instance/` folder. Uploaded files go into `temporary_uploads/`. Both folders are kept out of the GitHub repository because they contain local data.

## CSV requirements

For an analysis to work, your CSV file needs to:

- be a `.csv` file
- have column names in the first row
- contain at least three rows
- have two different numerical columns with no missing values
- contain some variation in both selected columns

## Run the tests

```bash
pytest
```

## Built with

- Python
- Flask
- SQLite
- pandas
- scikit-learn
- pytest
