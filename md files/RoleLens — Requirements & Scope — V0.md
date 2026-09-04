## Project Goal

Build a small application for physics students who work with laboratory measurements and repeatedly need to fit experimental data to a simple linear model.

For V0, the application will focus only on **simple linear regression**.

The application performs the numerical analysis and provides visual and quantitative evidence. The **student remains responsible for deciding whether the linear model is physically justified and whether the fit is scientifically meaningful**.

---

## Primary User

Physics students working with laboratory measurement data.

---

## Supported Model

V0 supports only the linear model

\[
y=b_1x+b_0
\]

where:

- \(b_1\) is the fitted slope.
- \(b_0\) is the fitted intercept.

Both slope and intercept are estimated from the data.

---

## Functional Requirements

### FR1 — CSV Input

The program accepts a CSV file where:

- the first row contains column names;
- subsequent rows contain the data.

Only CSV files are supported in V0.

### FR2 — X/Y Selection

After loading the CSV, the user chooses:

- one column as \(X\);
- one column as \(Y\).

### FR3 — Data Validation

After the user chooses \(X\) and \(Y\), the system verifies that:

- all selected X values are present;
- all selected Y values are present;
- all X values are numerical;
- all Y values are numerical.

If the selected data are invalid or contain missing values, the system should inform the user instead of attempting the regression.

Other columns in the CSV do not need to be numerical or complete because they are not used in the analysis.

### FR4 — Linear Regression Calculation

The system performs simple linear regression on the selected X and Y data using

\[
y=b_1x+b_0.
\]

It calculates:

- slope \(b_1\);
- intercept \(b_0\);
- coefficient of determination \(R^2\);
- RMSE.

### FR5 — Numerical Results

The application displays:

- slope;
- intercept;
- \(R^2\);
- RMSE.

### FR6 — Fit Visualization

The application displays a graph containing:

- the original experimental data as a scatter plot;
- the fitted linear regression line.

### FR7 — Residual Visualization

The application displays a residual plot showing the differences between the measured values and the fitted values.

For each point,

\[
r_i=y_i-\hat y_i.
\]

---

## V0 Design Principle

The application **does not automatically declare whether the model is good, bad, correct, or physically justified**.

It provides the student with:

- fitted parameters;
- quantitative fit metrics;
- visualizations;
- residual information.

The student interprets those results.

---

## Explicit V0 Limitations

V0 will **not** include:

- measurement uncertainties;
- weighted regression;
- automatic data transformations such as \(T\rightarrow T^2\);
- multiple linear regression;
- polynomial regression;
- nonlinear curve fitting;
- logistic regression;
- automatic outlier removal;
- automatic scientific interpretation;
- automatic model selection.

For transformations such as a pendulum analysis requiring \(T^2\), the student must prepare the transformed column before using the application.

---

## Future Possibilities

Possible later extensions include:

- measurement uncertainties and error bars;
- uncertainty in fitted parameters;
- weighted least squares;
- \(\chi^2\) analysis;
- multiple linear regression;
- polynomial fitting;
- nonlinear curve fitting;
- user-defined transformations;
- comparison of different models.

These are not requirements for V0.

---

## Edge Cases to Investigate Later

The following questions are deliberately postponed:

- What happens if every X value is identical?
- What minimum number of measurements should be required?
- How should `NaN` or infinite values be handled?
- Should the interface prevent users from selecting non-numerical columns, or allow the selection and then return a validation error?

These should be handled before the final release but do not need to block the initial architecture work.