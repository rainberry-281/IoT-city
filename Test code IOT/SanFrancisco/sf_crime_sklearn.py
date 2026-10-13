"""
Phát hiện loại tội phạm từ mô tả vụ việc tại San Francisco
Triển khai bằng Scikit-Learn (Chạy nhanh, độc lập, không cần Java/Spark)
Mô phỏng chính xác thuật toán từ Chương 11 của sách
"""

import sys
import csv
import os
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score, accuracy_score, classification_report
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    print("Vui lòng cài đặt scikit-learn để chạy file này: pip install scikit-learn")
    sys.exit(0)


def load_dataset(csv_path="sf_crime_dataset.csv"):
    """Đọc dữ liệu CSV và trích xuất hai cột: Descript và Category"""
    if not os.path.exists(csv_path):
        print(f"Không tìm thấy tệp {csv_path}. Đang chạy download_sf_data.py để tải...")
        from download_sf_data import download_sf_crime_data
        download_sf_crime_data(limit=5000)

    descriptions = []
    categories = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get("Descript", "").strip()
            cat = row.get("Category", "").strip()
            if desc and cat:
                descriptions.append(desc)
                categories.append(cat)

    return descriptions, categories


def main():
    print("=" * 80)
    print(" DỰ ĐOÁN LOẠI TỘI PHẠM SAN FRANCISCO (SCIKIT-LEARN PIPELINE)")
    print("=" * 80)

    # 1. Nạp dữ liệu
    print("\n[Bước 1] Đang nạp dữ liệu từ 'sf_crime_dataset.csv'...")
    descriptions, categories = load_dataset()
    print(f"Tổng số bản ghi hợp lệ: {len(descriptions)}")

    unique_categories = sorted(list(set(categories)))
    print(f"Số lượng danh mục tội phạm (Classes): {len(unique_categories)}")
    print("Một số danh mục tiêu biểu:", unique_categories[:8])

    # 2. Tiền xử lý văn bản: Tách từ & loại bỏ từ dừng giống như cấu hình PySpark
    print("\n[Bước 2] Tiền xử lý văn bản bằng CountVectorizer...")
    stop_words = ["http", "https", "amp", "rt", "t", "c", "the"]
    # Token pattern tương đương với RegexTokenizer pattern="\\W"
    vectorizer = CountVectorizer(
        token_pattern=r"(?u)\b\w+\b",
        stop_words=stop_words,
        max_features=10000,
        min_df=2
    )

    X = vectorizer.fit_transform(descriptions)
    print(f"Kích thước ma trận đặc trưng (Bag-of-Words): {X.shape}")

    # 3. Mã hóa nhãn Category thành số nguyên (tương đương StringIndexer)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(categories)

    # 4. Chia tập Train/Test (70% - 30%)
    print("\n[Bước 3] Chia tập dữ liệu 70% Train - 30% Test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=100, stratify=None
    )
    print(f"Số mẫu tập huấn luyện (Train): {X_train.shape[0]}")
    print(f"Số mẫu tập kiểm thử (Test)    : {X_test.shape[0]}")

    # 5. Huấn luyện mô hình Logistic Regression
    print("\n[Bước 4] Huấn luyện Logistic Regression (max_iter=50)...")
    model = LogisticRegression(max_iter=50, C=1.0, solver="lbfgs")
    model.fit(X_train, y_train)

    # 6. Dự đoán trên tập kiểm thử
    print("Đang đánh giá mô hình trên tập kiểm thử...")
    y_pred = model.predict(X_test)

    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    acc = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 65)
    print(" KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH")
    print("=" * 65)
    print(f" • Điểm F1 có trọng số (Weighted F1) : {weighted_f1:.4f} (~{weighted_f1 * 100:.2f}%)")
    print(f" • Độ chính xác chuẩn (Accuracy)     : {acc:.4f} (~{acc * 100:.2f}%)")

    # 7. Thử nghiệm dự đoán thực tế trên mô tả mới
    print("\n" + "=" * 65)
    print(" THỬ NGHIỆM DỰ ĐOÁN VỚI CÁC MÔ TẢ MỚI")
    print("=" * 65)
    sample_descriptions = [
        "STOLEN AUTOMOBILE, VEHICLE PARKED ON STREET",
        "BATTERY WITH SERIOUS BODILY INJURY",
        "PETTY THEFT FROM LOCKED VEHICLE",
        "MALICIOUS MISCHIEF, VANDALISM TO PROPERTY",
        "POSSESSION OF CONTROLLED SUBSTANCE FOR SALE"
    ]

    sample_vec = vectorizer.transform(sample_descriptions)
    sample_preds = model.predict(sample_vec)
    sample_labels = label_encoder.inverse_transform(sample_preds)

    for desc, pred_cat in zip(sample_descriptions, sample_labels):
        print(f"Mô tả: \"{desc}\"")
        print(f"  --> Dự đoán loại tội phạm: [{pred_cat}]\n")


if __name__ == "__main__":
    main()

