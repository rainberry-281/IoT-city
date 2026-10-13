"""
Chương trình thu thập dữ liệu Array of Things (AoT) và Cảm biến Môi trường Đô thị Chicago
Nguồn dữ liệu: Cổng Dữ liệu Mở Thành phố Chicago (https://data.cityofchicago.org)
Giao thức: Socrata Open Data API (SODA RESTful API)
"""

import sys
import json
import requests

# Đảm bảo hiển thị tiếng Việt chính xác trên Windows Console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Endpoint cho vị trí các nút cảm biến Array of Things (Dataset ID: 6rq2-yx28)
AOT_NODES_URL = "https://data.cityofchicago.org/resource/6rq2-yx28.json"

# Endpoint cho quan sát môi trường/thời tiết tự động theo thời gian thực (Dataset ID: k7hf-8y75)
OBSERVATIONS_URL = "https://data.cityofchicago.org/resource/k7hf-8y75.json"


def get_aot_nodes(limit=15, vsn=None):
    """
    Lấy danh sách các nút cảm biến (Nodes) Array of Things của Chicago
    Mỗi nút có một mã VSN (Vessel/Node Serial Number) duy nhất.
    """
    params = {"$limit": limit}
    if vsn:
        params["node_sensor_number"] = vsn

    print("\n" + "=" * 90)
    title = f"DANH SÁCH NÚT CẢM BIẾN ARRAY OF THINGS (Mã VSN: {vsn})" if vsn else "DANH SÁCH NÚT CẢM BIẾN ARRAY OF THINGS (CHICAGO)"
    print(f" {title}")
    print("=" * 90)

    try:
        response = requests.get(AOT_NODES_URL, params=params, timeout=10)
        response.raise_for_status()
        nodes = response.json()

        if not nodes:
            print("Không tìm thấy nút cảm biến nào phù hợp.")
            return []

        print(f"Tổng số nút lấy được: {len(nodes)}")
        header = f"{'Mã VSN':<10} | {'Tên trạm / Vị trí':<35} | {'Trạng thái':<10} | {'Tọa độ (Vĩ độ, Kinh độ)'}"
        print(header)
        print("-" * 90)

        for n in nodes:
            vsn_code = n.get("node_sensor_number", "N/A")
            name = (n.get("name") or "N/A")[:34]
            status = n.get("status", "N/A")
            lat = n.get("latitude", "")
            lon = n.get("longitude", "")
            coords = f"({lat}, {lon})" if lat and lon else "N/A"
            print(f"{vsn_code:<10} | {name:<35} | {status:<10} | {coords}")

        return nodes
    except Exception as e:
        print(f"Lỗi khi truy vấn danh sách nút: {e}")
        return []


def get_live_sensor_observations(limit=5):
    """
    Lấy các quan sát thời gian thực từ mạng lưới cảm biến môi trường đô thị Chicago
    Các thông số gồm: Nhiệt độ, độ ẩm, áp suất khí quyển, bức xạ mặt trời, gió...
    """
    params = {"$limit": limit}

    print("\n" + "=" * 90)
    print(" DỮ LIỆU QUAN SÁT THỜI GIAN THỰC TỪ CẢM BIẾN MÔI TRƯỜNG ĐÔ THỊ (CHICAGO)")
    print("=" * 90)

    try:
        response = requests.get(OBSERVATIONS_URL, params=params, timeout=10)
        response.raise_for_status()
        observations = response.json()

        if not observations:
            print("Không có bản ghi quan sát nào.")
            return []

        print(f"Nhận được {len(observations)} bản ghi quan sát môi trường:")
        for record in observations:
            station = record.get("station_name", "N/A")
            timestamp = record.get("measurement_timestamp_label") or record.get("measurement_timestamp", "N/A")
            temp = record.get("air_temperature", "N/A")
            humidity = record.get("humidity", "N/A")
            pressure = record.get("barometric_pressure", "N/A")
            solar = record.get("solar_radiation", "N/A")
            wind_speed = record.get("wind_speed", "N/A")

            print(f"\n[Trạm cảm biến: {station}] - Thời gian đo: {timestamp}")
            print(f"  • Nhiệt độ không khí   : {temp} °C")
            print(f"  • Độ ẩm tương đối     : {humidity} %")
            print(f"  • Áp suất khí quyển    : {pressure} hPa")
            print(f"  • Bức xạ mặt trời      : {solar} W/m²")
            print(f"  • Tốc độ gió           : {wind_speed} m/s")

        return observations
    except Exception as e:
        print(f"Lỗi khi truy vấn dữ liệu quan sát: {e}")
        return []


if __name__ == "__main__":
    print("Bắt đầu truy vấn dữ liệu dự án Chicago (Open Data Portal)...")

    # 1. Lấy danh sách tổng quan các nút cảm biến AoT
    get_aot_nodes(limit=10)

    # 2. Truy vấn một nút cảm biến cụ thể theo mã VSN (ví dụ mã '06E' tại UChicago Logan Center)
    get_aot_nodes(vsn="06E")

    # 3. Lấy dữ liệu quan sát môi trường thời gian thực (nhiệt độ, độ ẩm, áp suất, v.v.)
    get_live_sensor_observations(limit=3)

