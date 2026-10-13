"""
Chương trình lưu trữ dữ liệu thời gian thực MARTA vào cơ sở dữ liệu SQLite
API Key: e0c03f40-8c8b-4186-9df6-c1d04aebc1f6
"""

import os
import sys
import sqlite3
import requests

# Đảm bảo hiển thị UTF-8 trên Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_KEY = "e0c03f40-8c8b-4186-9df6-c1d04aebc1f6"
DB_NAME = "marta_transit.db"
API_URL = "https://developerservices.itsmarta.com:18096/itsmarta/railrealtimearrivals/developerservices/traindata"


def init_database(db_name=DB_NAME):
    """Khởi tạo cấu trúc bảng trong SQLite"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS train_arrivals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_id TEXT,
            line TEXT,
            direction TEXT,
            station TEXT,
            destination TEXT,
            waiting_time TEXT,
            waiting_seconds INTEGER,
            next_arrival TEXT,
            event_time TEXT,
            delay TEXT,
            latitude REAL,
            longitude REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save_marta_data_to_sqlite():
    """Lấy dữ liệu từ API và lưu vào database SQLite"""
    print(f"Đang kết nối tới API MARTA...")
    response = requests.get(API_URL, params={"apiKey": API_KEY}, timeout=10)
    response.raise_for_status()
    train_records = response.json()
    print(f"Nhận được {len(train_records)} bản ghi từ API.")

    conn = init_database()
    cursor = conn.cursor()

    inserted_count = 0
    for record in train_records:
        cursor.execute("""
            INSERT INTO train_arrivals (
                train_id, line, direction, station, destination,
                waiting_time, waiting_seconds, next_arrival,
                event_time, delay, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.get("TRAIN_ID"),
            record.get("LINE"),
            record.get("DIRECTION"),
            record.get("STATION"),
            record.get("DESTINATION"),
            record.get("WAITING_TIME"),
            int(record.get("WAITING_SECONDS", 0)) if record.get("WAITING_SECONDS") else None,
            record.get("NEXT_ARR"),
            record.get("EVENT_TIME"),
            record.get("DELAY"),
            float(record.get("LATITUDE", 0)) if record.get("LATITUDE") else None,
            float(record.get("LONGITUDE", 0)) if record.get("LONGITUDE") else None
        ))
        inserted_count += 1

    conn.commit()
    print(f"Đã lưu thành công {inserted_count} bản ghi vào file '{DB_NAME}'.")

    # Truy vấn thử dữ liệu vừa lưu
    cursor.execute("SELECT train_id, line, station, destination, waiting_time FROM train_arrivals LIMIT 5")
    rows = cursor.fetchall()
    print("\n5 bản ghi mẫu từ cơ sở dữ liệu SQLite:")
    for row in rows:
        print(f"Tàu {row[0] or 'N/A'} | Tuyến {row[1]} | Ga: {row[2]} -> {row[3]} ({row[4]})")

    conn.close()


if __name__ == "__main__":
    save_marta_data_to_sqlite()

