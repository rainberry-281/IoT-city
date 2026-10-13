"""
Tải dữ liệu tội phạm San Francisco từ Cổng dữ liệu mở datasf.org (data.sfgov.org)
Dataset ID: tmnf-yvry (Police Department Incident Reports: Historical 2003 to May 2018)
"""

import sys
import csv
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DATASET_URL = "https://data.sfgov.org/resource/tmnf-yvry.json"
OUTPUT_FILE = "sf_crime_dataset.csv"


def download_sf_crime_data(limit=5000):
    """Tải dữ liệu tội phạm thực tế từ San Francisco Open Data Portal và lưu ra CSV"""
    print(f"Đang tải {limit} bản ghi từ Cổng dữ liệu mở San Francisco (datasf.org)...")
    params = {
        "$limit": limit,
        "$where": "category IS NOT NULL AND descript IS NOT NULL"
    }

    try:
        response = requests.get(DATASET_URL, params=params, timeout=20)
        response.raise_for_status()
        records = response.json()
        print(f"Tải thành công {len(records)} bản ghi!")

        # Chuẩn hóa cột khớp với yêu cầu của giáo trình:
        # Dates, Category, Descript, DayOfWeek, PdDistrict, Resolution, Address, X, Y
        headers = ["Dates", "Category", "Descript", "DayOfWeek", "PdDistrict", "Resolution", "Address", "X", "Y"]

        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for r in records:
                row = [
                    r.get("date", ""),
                    r.get("category", ""),
                    r.get("descript", ""),
                    r.get("dayofweek", ""),
                    r.get("pddistrict", ""),
                    r.get("resolution", ""),
                    r.get("address", ""),
                    r.get("x", ""),
                    r.get("y", "")
                ]
                writer.writerow(row)

        print(f"Đã lưu dữ liệu vào tệp: '{OUTPUT_FILE}' thành công.")
        return OUTPUT_FILE
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {e}")
        return None


if __name__ == "__main__":
    download_sf_crime_data(limit=5000)

