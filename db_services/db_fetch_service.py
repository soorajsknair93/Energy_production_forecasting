import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------------------------------
# DB CONFIG
# ------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "database": "energy_db",
    "user": "sooraj",
    "password": "Quest1234",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# ------------------------------------------
# FETCH FEATURE COLUMNS FROM DB
# ------------------------------------------
def fetch_feature_columns():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT feature_name FROM feature_columns ORDER BY id;")
        cols = [row[0] for row in cur.fetchall()]
        conn.close()
        return cols
    except Exception as e:
        print("Error fetching feature columns:", e)
        return []

# ------------------------------------------
# FETCH LAST VALUES / DATE FROM DB
# ------------------------------------------
def fetch_last_values():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT last_values, last_date FROM training_snapshot ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        conn.close()
        if row:
            last_values, last_date = row
            last_date = pd.to_datetime(last_date)
            return list(last_values), last_date
        else:
            raise ValueError("No training snapshot found in DB.")
    except Exception as e:
        print("Error fetching last values:", e)
        raise e

