"""
Chương trình thu thập dữ liệu thời gian thực từ Cơ quan Vận tải Nhanh Đô thị Atlanta (MARTA)
API Key: e0c03f40-8c8b-4186-9df6-c1d04aebc1f6
"""

import os
import sys
import json
import requests
from marta.api import get_buses, get_trains

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Thiết lập API Key cho MARTA qua biến môi trường
API_KEY = "e0c03f40-8c8b-4186-9df6-c1d04aebc1f6"
os.environ["MARTA_API_KEY"] = API_KEY


def display_trains(train_list, title="Danh sách chuyến tàu"):
    """Hiển thị danh sách tàu theo định dạng bảng dễ đọc"""
    print("=" * 85)
    print(f" {title} (Tổng số: {len(train_list)})")
    print("=" * 85)
    if not train_list:
        print("Không tìm thấy chuyến tàu nào phù hợp với bộ lọc.")
        return

    header = f"{'Mã tàu':<10} | {'Tuyến':<7} | {'Hướng':<6} | {'Ga hiện tại':<25} | {'Điểm đến':<15} | {'Dự kiến đến':<12}"
    print(header)
    print("-" * 85)

    for train in train_list[:10]:  # Giới hạn in 10 chuyến đầu để dễ quan sát
        train_id = train.train_id or "N/A"
        line = train.line or "N/A"
        direction = train.direction or "N/A"
        station = (train.station or "N/A")[:24]
        destination = (train.destination or "N/A")[:14]
        waiting = f"{train.waiting_time} ({train.next_arrival})"

        print(f"{train_id:<10} | {line:<7} | {direction:<6} | {station:<25} | {destination:<15} | {waiting:<12}")

    if len(train_list) > 10:
        print(f"... và còn {len(train_list) - 10} chuyến tàu khác.")
    print()


def fetch_using_marta_lib():
    """Lấy dữ liệu thời gian thực sử dụng thư viện MARTA-Python"""
    print("\n>>> ĐANG LẤY DỮ LIỆU BẰNG THƯ VIỆN MARTA-PYTHON <<<")

    # 1. Lấy danh sách tất cả các chuyến tàu đang hoạt động
    print("\n1. Đang truy vấn tất cả các chuyến tàu...")
    all_trains = get_trains()
    display_trains(all_trains, "Tất cả các chuyến tàu")

    # 2. Lấy danh sách tàu theo tuyến (ví dụ: Tuyến Đỏ - RED Line)
    print("\n2. Đang truy vấn các chuyến tàu thuộc tuyến Đỏ (Red Line)...")
    trains_red = get_trains(line='red')
    display_trains(trains_red, "Tuyến Đỏ (RED Line)")

    # 3. Lấy danh sách tàu tại ga Midtown Station
    print("\n3. Đang truy vấn các chuyến tàu tại ga Midtown...")
    trains_station = get_trains(station='Midtown Station')
    display_trains(trains_station, "Ga Midtown (Midtown Station)")

    # 4. Lấy danh sách tàu theo điểm đến Doraville
    print("\n4. Đang truy vấn các chuyến tàu có điểm đến Doraville...")
    trains_doraville = get_trains(destination='Doraville')
    display_trains(trains_doraville, "Tàu hướng về Doraville")

    # 5. Lấy danh sách tàu kết hợp bộ lọc: tuyến Xanh (Blue), ga Five Points và điểm đến Indian Creek
    print("\n5. Đang truy vấn kết hợp (Tuyến Blue, Ga Five Points, Điểm đến Indian Creek)...")
    trains_all = get_trains(
        line='blue',
        station='Five Points Station',
        destination='Indian Creek'
    )
    display_trains(trains_all, "Tuyến Blue - Five Points Station -> Indian Creek")

    # 6. Thử truy vấn danh sách xe buýt theo cú pháp giáo trình
    print("\n6. Đang thử truy vấn danh sách xe buýt (get_buses)...")
    all_buses = get_buses()
    print(f"-> Kết quả: Nhận được {len(all_buses)} xe buýt.")

    # 7. Truy vấn xe buýt theo tuyến số 1
    print("\n7. Đang thử truy vấn xe buýt tuyến số 1 (route=1)...")
    buses_route = get_buses(route=1)
    print(f"-> Kết quả: Nhận được {len(buses_route)} xe buýt trên tuyến 1.")


def fetch_using_rest_api_directly():
    """
    Lấy dữ liệu trực tiếp bằng REST API qua thư viện requests
    Endpoint chính thức của MARTA: https://developerservices.itsmarta.com:18096/itsmarta/railrealtimearrivals/developerservices/traindata
    """
    print("\n>>> ĐANG LẤY DỮ LIỆU TRỰC TIẾP QUA REST API CỦA MARTA (REQUESTS) <<<")
    endpoint = "https://developerservices.itsmarta.com:18096/itsmarta/railrealtimearrivals/developerservices/traindata"
    params = {"apiKey": API_KEY}

    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Truy vấn API thành công! Nhận được {len(data)} bản ghi thời gian thực.")

        # Hiển thị mẫu bản ghi JSON đầu tiên
        if data:
            print("\nMẫu 1 bản ghi JSON gốc:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        return data
    except Exception as e:
        print(f"Lỗi khi gọi REST API trực tiếp: {e}")
        return []


if __name__ == "__main__":
    print(f"Khởi động chương trình với MARTA API Key: {API_KEY}")

    # Chạy phương thức 1: Sử dụng thư viện marta-python như trong giáo trình
    fetch_using_marta_lib()

    # Chạy phương thức 2: Gọi REST API trực tiếp bằng requests
    fetch_using_rest_api_directly()
