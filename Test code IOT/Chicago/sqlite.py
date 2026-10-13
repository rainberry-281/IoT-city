"""
Chương trình lưu trữ dữ liệu Array of Things và Cảm biến Chicago vào SQLite
Nguồn dữ liệu: data.cityofchicago.org
"""

import sys
import sqlite3
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DB_NAME = "chicago_iot.db"
AOT_NODES_URL = "https://data.cityofchicago.org/resource/6rq2-yx28.json"
OBSERVATIONS_URL = "https://data.cityofchicago.org/resource/k7hf-8y75.json"


def init_database(db_name=DB_NAME):
    """Khởi tạo cấu trúc các bảng cho nút và quan sát cảm biến trong SQLite"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Bảng lưu trữ thông tin Nút cảm biến (Nodes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aot_nodes (
            id TEXT PRIMARY KEY,
            vsn TEXT,
            name TEXT,
            status TEXT,
            north_south_street TEXT,
            east_west_street TEXT,
            latitude REAL,
            longitude REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bảng lưu trữ Quan sát cảm biến theo thời gian (Observations) - Quan hệ 1-N
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_id TEXT UNIQUE,
            station_name TEXT,
            measurement_timestamp TEXT,
            air_temperature REAL,
            humidity REAL,
            barometric_pressure REAL,
            solar_radiation REAL,
            wind_speed REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return conn


def save_chicago_data_to_sqlite():
    """Lấy dữ liệu từ Chicago Open Data Portal và lưu vào SQLite"""
    conn = init_database()
    cursor = conn.cursor()

    # 1. Lưu danh sách Nút cảm biến AoT
    print("1. Đang tải và lưu danh sách nút cảm biến AoT...")
    try:
        res_nodes = requests.get(AOT_NODES_URL, params={"$limit": 100}, timeout=10)
        res_nodes.raise_for_status()
        nodes = res_nodes.json()

        for n in nodes:
            cursor.execute("""
                INSERT OR REPLACE INTO aot_nodes (
                    id, vsn, name, status, north_south_street, east_west_street, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                n.get("id"),
                n.get("node_sensor_number"),
                n.get("name"),
                n.get("status"),
                n.get("north_south_street"),
                n.get("east_west_street"),
                float(n.get("latitude", 0)) if n.get("latitude") else None,
                float(n.get("longitude", 0)) if n.get("longitude") else None
            ))

        conn.commit()
        print(f"-> Đã lưu {len(nodes)} nút cảm biến vào bảng 'aot_nodes'.")
    except Exception as e:
        print(f"Lỗi khi lưu nút: {e}")

    # 2. Lưu các quan sát cảm biến môi trường
    print("\n2. Đang tải và lưu các quan sát cảm biến thời gian thực...")
    try:
        res_obs = requests.get(OBSERVATIONS_URL, params={"$limit": 50}, timeout=10)
        res_obs.raise_for_status()
        observations = res_obs.json()

        obs_count = 0
        for obs in observations:
            m_id = obs.get("measurement_id")
            if not m_id:
                continue
            cursor.execute("""
                INSERT OR IGNORE INTO sensor_observations (
                    measurement_id, station_name, measurement_timestamp,
                    air_temperature, humidity, barometric_pressure,
                    solar_radiation, wind_speed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m_id,
                obs.get("station_name"),
                obs.get("measurement_timestamp"),
                float(obs.get("air_temperature", 0)) if obs.get("air_temperature") else None,
                float(obs.get("humidity", 0)) if obs.get("humidity") else None,
                float(obs.get("barometric_pressure", 0)) if obs.get("barometric_pressure") else None,
                float(obs.get("solar_radiation", 0)) if obs.get("solar_radiation") else None,
                float(obs.get("wind_speed", 0)) if obs.get("wind_speed") else None
            ))
            obs_count += 1

        conn.commit()
        print(f"-> Đã lưu {obs_count} quan sát cảm biến vào bảng 'sensor_observations'.")
    except Exception as e:
        print(f"Lỗi khi lưu quan sát: {e}")

    # Truy vấn kiểm tra dữ liệu
    print("\nKiểm tra dữ liệu mẫu từ SQLite:")
    cursor.execute("SELECT vsn, name, status, latitude, longitude FROM aot_nodes LIMIT 3")
    for r in cursor.fetchall():
        print(f"  • Nút VSN: {r[0]} | Tên: {r[1]} | Trạng thái: {r[2]}")

    cursor.execute("SELECT station_name, air_temperature, humidity, measurement_timestamp FROM sensor_observations LIMIT 2")
    for r in cursor.fetchall():
        print(f"  • Quan sát: Trạm {r[0]} | Nhiệt độ: {r[1]}°C | Độ ẩm: {r[2]}% | Thời gian: {r[3]}")

    conn.close()


if __name__ == "__main__":
    save_chicago_data_to_sqlite()

