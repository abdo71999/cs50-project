import pandas as pd
from pandas.api.types import is_numeric_dtype, is_bool_dtype
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, root_mean_squared_error


def load_dataset(file_path):
    return pd.read_csv(file_path)


def get_col_names(data_frame):
    return data_frame.columns.to_list()


def has_missing_values(data_frame, column_name):
    return data_frame[column_name].isna().any()


def is_numeric_column(data_frame, column_name):
    return is_numeric_dtype(data_frame[column_name]) and not is_bool_dtype(
        data_frame[column_name]
    )


def has_enough_rows(data_frame):
    return len(data_frame) >= 3


def has_variation(data_frame, column_name):
    return data_frame[column_name].nunique() >= 2


def fit_linear_regression(data_frame, x_column, y_column):
    model = LinearRegression()
    return model.fit(data_frame[[x_column]], data_frame[y_column])


def calculate_metrics(actual, predicted):
    """Return R² and RMSE for observed and predicted values."""

    return r2_score(actual, predicted), root_mean_squared_error(actual, predicted)


def y_table(actual_y, predicted_y):
    result_frame = pd.DataFrame(
        {
            "actual_y": actual_y.to_numpy(),
            "predicted_y": predicted_y,
        }
    )

    result_frame["residual"] = result_frame["actual_y"] - result_frame["predicted_y"]

    return result_frame.to_dict(orient="records")
