"""
Phát hiện loại tội phạm từ dữ liệu San Francisco bằng Apache PySpark
Dựa trên Chương 11: AI for Smart Cities IoT (Hands-On Artificial Intelligence for IoT)

Các cải tiến so với bản in trong sách:
1. Sửa cấu hình RAM (thay vì 136GB RAM gây sập máy cá nhân, đặt mức an toàn 2GB-4GB).
2. Thêm import MulticlassClassificationEvaluator (bản in bị thiếu).
3. Đánh giá cả F1-score có trọng số và Accuracy thực tế.
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from pyspark.sql import SparkSession
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression as LR
    from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer, StringIndexer
    from pyspark.ml.evaluation import MulticlassClassificationEvaluator
except ImportError:
    print("CHÚ Ý: Chưa tìm thấy thư viện PySpark trên máy tính.")
    print("Để chạy file này với Spark, hãy cài đặt: pip install pyspark")
    print("Hoặc bạn có thể chạy file 'sf_crime_sklearn.py' sử dụng Python tiêu chuẩn mà không cần Spark/Java.")
    sys.exit(0)


def main():
    print("=" * 80)
    print(" KHỞI ĐỘNG CHƯƠNG TRÌNH DỰ ĐOÁN TỘI PHẠM SAN FRANCISCO (PYSPARK ML)")
    print("=" * 80)

    # 1. Khởi tạo phiên Spark an toàn cho máy cá nhân
    print("\n[Bước 1] Đang khởi tạo SparkSession...")
    spark = SparkSession.builder \
        .appName("Crime Category Prediction - San Francisco") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    # 2. Đọc bộ dữ liệu từ tệp CSV
    csv_file = "sf_crime_dataset.csv"
    if not os.path.exists(csv_file):
        print(f"Lỗi: Không tìm thấy tệp {csv_file}. Vui lòng chạy download_sf_data.py trước!")
        return

    print(f"\n[Bước 2] Đang nạp dữ liệu từ tệp '{csv_file}'...")
    data = spark.read.format("csv") \
        .options(header="true", inferSchema="true") \
        .load(csv_file)

    print("Các cột ban đầu trong dữ liệu:", data.columns)

    # 3. Lọc chọn 2 trường Category và Descript
    print("\n[Bước 3] Lọc bỏ các cột không cần thiết, chỉ giữ lại 'Category' và 'Descript'...")
    drop_data = ['Dates', 'DayOfWeek', 'PdDistrict', 'Resolution', 'Address', 'X', 'Y']
    data = data.select([col for col in data.columns if col not in drop_data]).dropna()

    print("Mẫu 5 dòng dữ liệu đầu tiên:")
    data.show(5, truncate=False)

    # 4. Tiền xử lý văn bản bằng Pipeline
    print("\n[Bước 4] Thiết lập Pipeline tiền xử lý văn bản (Tokenizer -> StopWords -> CountVectorizer -> StringIndexer)...")
    re_tokenizer = RegexTokenizer(inputCol="Descript", outputCol="words", pattern="\\W")
    stop_words = ["http", "https", "amp", "rt", "t", "c", "the"]
    stop_words_remover = StopWordsRemover(inputCol="words", outputCol="filtered").setStopWords(stop_words)
    count_vectors = CountVectorizer(inputCol="filtered", outputCol="features", vocabSize=10000, minDF=5)
    label_string_idx = StringIndexer(inputCol="Category", outputCol="label")

    pipeline = Pipeline(stages=[re_tokenizer, stop_words_remover, count_vectors, label_string_idx])

    print("Đang khớp (fit) Pipeline vào dữ liệu...")
    pipeline_fit = pipeline.fit(data)
    dataset = pipeline_fit.transform(data)

    print("Mẫu dữ liệu sau khi biến đổi đặc trưng:")
    dataset.select("Category", "Descript", "label", "features").show(5, truncate=50)

    # 5. Chia tập huấn luyện (70%) và tập kiểm thử (30%)
    print("\n[Bước 5] Chia tập Train / Test (70% - 30%)...")
    (training_data, test_data) = dataset.randomSplit([0.7, 0.3], seed=100)
    print("Số mẫu tập huấn luyện (Train):", training_data.count())
    print("Số mẫu tập kiểm thử (Test)    :", test_data.count())

    # 6. Huấn luyện mô hình Logistic Regression và đánh giá
    print("\n[Bước 6] Đang huấn luyện mô hình Logistic Regression (maxIter=20, regParam=0.3)...")
    logistic_regressor = LR(maxIter=20, regParam=0.3, elasticNetParam=0)
    model = logistic_regressor.fit(training_data)

    print("Đang dự đoán trên tập kiểm thử (Test Data)...")
    predictions = model.transform(test_data)

    # Đánh giá bằng MulticlassClassificationEvaluator
    # Mặc định theo sách (Weighted F1-score)
    evaluator_f1 = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="label", metricName="f1")
    score_f1 = evaluator_f1.evaluate(predictions)

    # Độ chính xác chuẩn (Accuracy)
    evaluator_acc = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="label", metricName="accuracy")
    score_acc = evaluator_acc.evaluate(predictions)

    print("\n" + "=" * 60)
    print(" KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH")
    print("=" * 60)
    print(f" • Điểm F1 có trọng số (Weighted F1) : {score_f1:.4f} (~{score_f1 * 100:.2f}%)")
    print(f" • Độ chính xác chuẩn (Accuracy)     : {score_acc:.4f} (~{score_acc * 100:.2f}%)")

    spark.stop()
    print("\nHoàn tất phiên làm việc với Spark.")


if __name__ == "__main__":
    main()

