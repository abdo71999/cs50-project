import pytest
import pandas as pd
from data_processing import fit_linear_regression, calculate_metrics, y_table
from pathlib import Path

# test perfect data


def test_slope_and_intercept():
    data_path = Path(__file__).parent / "perfect_linear_test.csv"
    data_frame = pd.read_csv(data_path)
    model = fit_linear_regression(data_frame, "x", "y")

    assert model.coef_[0] == pytest.approx(2)
    assert model.intercept_ == pytest.approx(1)


def test_metrics():
    actual = [2, 4, 6, 8]
    predicted = [2, 4, 6, 8]

    r_squared, rmse = calculate_metrics(actual, predicted)

    assert rmse == pytest.approx(0)
    assert r_squared == pytest.approx(1)


# imperfect data
def test_imperfect():
    actual_imperfect = [1, 2, 3]
    predicted_imperfect = [1, 2, 4]

    r_squared, rmse = calculate_metrics(actual_imperfect, predicted_imperfect)

    assert rmse == pytest.approx(0.577350269)
    assert r_squared == pytest.approx(0.5)


# test y_table
def test_y_table():
    actual = pd.Series([1, 2])
    predicted = [1.5, 1.5]
    residuals = [-0.5, 0.5]

    table = y_table(actual, predicted)

    for index, entry in enumerate(table):
        assert entry["actual_y"] == pytest.approx(actual[index])
        assert entry["predicted_y"] == pytest.approx(predicted[index])
        assert entry["residual"] == pytest.approx(residuals[index])


