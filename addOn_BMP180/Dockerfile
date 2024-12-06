# Sử dụng image Python cơ bản
FROM python:3.9-slim

# Cài đặt các gói cần thiết cho giao tiếp I2C và các thư viện hệ thống
RUN apt-get update && \
    apt-get install -y \
    i2c-tools \
    python3-smbus \
    && rm -rf /var/lib/apt/lists/*

# Sao chép mã Python và file requirements.txt vào container
COPY read_bmp180.py /app/read_bmp180.py
COPY requirements.txt /app/requirements.txt

# Đặt thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện Python được liệt kê trong requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Thiết lập lệnh mặc định khi chạy container
CMD ["python3", "read_bmp180.py"]
