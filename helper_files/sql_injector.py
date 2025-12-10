import psycopg2
import pickle

DB_CONFIG = {
    "host": "localhost",
    "database": "energy_db",
    "user": "sooraj",
    "password": "Quest1234",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Load pickle files
with open("./ai_modules/models/feature_columns.pkl", "rb") as f:
    feature_cols = pickle.load(f)

with open("./ai_modules/models/training_stats.pkl", "rb") as f:
    stats = pickle.load(f)

last_values = stats["last_values"]
last_date = stats["last_date"]

# Insert last_values / last_date
try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Clear old snapshot
    cur.execute("DELETE FROM training_snapshot;")
    
    # Insert snapshot
    cur.execute(
        "INSERT INTO training_snapshot (last_date, last_values) VALUES (%s, %s);",
        (last_date, last_values)
    )
    
    conn.commit()
    print("Training snapshot inserted.")
    
except Exception as e:
    print("DB Error:", e)
finally:
    cur.close()
    conn.close()

# Insert feature columns
try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Clear old features
    cur.execute("DELETE FROM feature_columns;")
    
    # Insert each feature
    for col in feature_cols:
        cur.execute(
            "INSERT INTO feature_columns (feature_name) VALUES (%s);",
            (col,)
        )
    
    conn.commit()
    
except Exception as e:
    print("DB Error:", e)
finally:
    cur.close()
    conn.close()
