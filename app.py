# from flask import Flask, render_template, request, send_file
# import os
# from api_services.forecasting_service import forecast_energy,detect_anomalies,plot_forecast,plot_anomalies

# app = Flask(__name__)

# # ---------------------------------------------------
# #REST ROUTES
# # ---------------------------------------------------
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         start_date = request.form.get("start_date")
#         end_date = request.form.get("end_date")
#         threshold = float(request.form.get("threshold"))

#         # Run forecasting
#         df_forecast = forecast_energy(start_date, end_date)
#         df_anomaly = detect_anomalies(df_forecast, threshold=threshold)

#         # Save csv
#         df_forecast.to_csv("forecast_output.csv", index=False)
#         df_anomaly.to_csv("forecast_anomaly_output.csv", index=False)

#         # Generate plots
#         plot_forecast(df_forecast)
#         plot_anomalies(df_anomaly)

#         return render_template(
#             "index.html",
#             forecast_img="static/forecast_plot.png",
#             anomaly_img="static/forecast_anomalies.png",
#             show_results=True
#         )

#     return render_template("index.html", show_results=False)


# @app.route("/download/<file>")
# def download(file):
#     return send_file(file, as_attachment=True)


# # ---------------------------------------------------
# # RUN APP
# # ---------------------------------------------------
# if __name__ == "__main__":
#     if not os.path.exists("static"):
#         os.makedirs("static")
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import threading

from api_services.forecasting_service import (
    forecast_energy,
    detect_anomalies,
    plot_forecast,
    plot_anomalies
)

app = Flask(__name__)

# Dictionary to track background jobs
jobs = {}

# ---------------------------------------------------
# Background job
# ---------------------------------------------------
def run_forecast_job(job_id, start_date, end_date, threshold):
    jobs[job_id] = {"status": "running"}

    # Run forecasting + anomaly detection
    df_forecast = forecast_energy(start_date, end_date)
    df_anomaly = detect_anomalies(df_forecast, threshold=threshold, window=7)

    # File paths
    forecast_csv = f"static/{job_id}_forecast.csv"
    anomaly_csv = f"static/{job_id}_anomaly.csv"
    forecast_img = f"static/{job_id}_forecast.png"
    anomaly_img = f"static/{job_id}_anomaly.png"

    df_forecast.to_csv(forecast_csv, index=False)
    df_anomaly.to_csv(anomaly_csv, index=False)

    plot_forecast(df_forecast, output=forecast_img)
    plot_anomalies(df_anomaly, output=anomaly_img)

    # Save job results
    jobs[job_id] = {
        "status": "completed",
        "forecast_img": forecast_img,
        "anomaly_img": anomaly_img,
        "forecast_csv": forecast_csv,
        "anomaly_csv": anomaly_csv
    }


# ---------------------------------------------------
# Main Page
# ---------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------
# Start async job
# ---------------------------------------------------
@app.route("/run_async", methods=["POST"])
def run_async():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    threshold = float(request.form.get("threshold"))

    job_id = str(uuid.uuid4())

    thread = threading.Thread(
        target=run_forecast_job,
        args=(job_id, start_date, end_date, threshold)
    )
    thread.start()

    return jsonify({"job_id": job_id, "status": "started"})


# ---------------------------------------------------
# Check job status
# ---------------------------------------------------
@app.route("/job_status/<job_id>")
def job_status(job_id):
    return jsonify(jobs.get(job_id, {"status": "not_found"}))


# ---------------------------------------------------
# Download files
# ---------------------------------------------------
@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)


# ---------------------------------------------------
# Run Flask app
# ---------------------------------------------------
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True)

