## Request 1
REQUEST 1
─────────

Browser uploads pendulum.csv
        ↓
Server generates random ID:
4f8c...e21
        ↓
Server saves:
temporary_uploads/4f8c...e21.csv
        ↓
Server stores:
session["upload_id"] = "4f8c...e21"
        ↓
Server reads column names
        ↓
Server sends HTML with X/Y dropdowns


## Request 2
1. Browser submits selected X and Y.

2. Flask reads the upload ID associated
   with the current session.

3. Flask finds the corresponding
   temporary CSV on the server.

4. Flask reads the selected X and Y columns.

5. Flask verifies:
      - no missing X/Y values
      - X is numerical
      - Y is numerical

6. If validation fails:
      return an error to the user.

7. If validation succeeds:
      perform linear regression.

8. Calculate:
      b₁
      b₀
      R²
      RMSE
      predicted values
      residuals

9. Generate:
      fitted-line plot
      residual plot

10. Return the results page.
