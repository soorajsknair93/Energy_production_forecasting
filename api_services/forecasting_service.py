import pandas as pd
import numpy as np
import joblib
import pickle
from datetime import timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from db_services.db_fetch_service import fetch_feature_columns,fetch_last_values

# Load model and metadata
model = joblib.load("./ai_modules/models/energy_model.pkl")

feature_cols = fetch_feature_columns()
last_values, last_date = fetch_last_values()

# ---------------------------------------------------
# FORECAST FUNCTION
# ---------------------------------------------------
def forecast_energy(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if start_date <= last_date:
        raise ValueError(
            f"Start date must be after last training date {last_date.date()}"
        )

    forecasts = []
    history = list(last_values)

    current_date = start_date
    while current_date <= end_date:

        row = {
            "Year": current_date.year,
            "Month": current_date.month,
            "Day": current_date.day,
            "DayOfWeek": current_date.dayofweek,
            "Quarter": current_date.quarter,
            "DayOfYear": current_date.timetuple().tm_yday,
            "WeekOfYear": current_date.isocalendar()[1]
        }

        # Lag
        for lag in [1, 7, 30, 90]:
            row[f"lag_{lag}"] = history[-lag]

        # Rolling
        for window in [7, 30, 90]:
            row[f"rolling_mean_{window}"] = np.mean(history[-window:])
            row[f"rolling_std_{window}"] = np.std(history[-window:])

        X = pd.DataFrame([row])[feature_cols]
        pred = model.predict(X)[0]

        forecasts.append([current_date, pred])
        history.append(pred)

        current_date += timedelta(days=1)

    return pd.DataFrame(forecasts, columns=["Date", "Predicted_Energy_Production"])


# ---------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------
def detect_anomalies(df, threshold=2.5, window=7):
    df = df.copy()
    df["rolling_mean"] = df["Predicted_Energy_Production"].rolling(window).mean()
    df["rolling_std"] = df["Predicted_Energy_Production"].rolling(window).std()
    df["z_score"] = (df["Predicted_Energy_Production"] - df["rolling_mean"]) / df["rolling_std"]
    df["Anomaly"] = df["z_score"].abs() > threshold
    return df


# ---------------------------------------------------
# PLOTTING FUNCTIONS (with custom file output)
# ---------------------------------------------------
def plot_forecast(df, output="static/forecast_plot.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Predicted_Energy_Production"], label="Forecast", linewidth=2)
    plt.xlabel("Date")
    plt.ylabel("Energy Production")
    plt.title("Forecasted Renewable Energy Production")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_anomalies(df, output="static/forecast_anomalies.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Predicted_Energy_Production"], label="Forecast", linewidth=2)

    anomalies = df[df["Anomaly"] == True]
    if not anomalies.empty:
        plt.scatter(anomalies["Date"], anomalies["Predicted_Energy_Production"],
                    color="red", label="Anomaly", s=80)

    plt.xlabel("Date")
    plt.ylabel("Energy Production")
    plt.title("Forecast with Anomaly Detection")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
