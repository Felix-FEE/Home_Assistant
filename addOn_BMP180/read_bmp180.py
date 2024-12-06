import smbus
import time
import requests
import os

# Địa chỉ I2C của cảm biến BMP180
BMP180_ADDRESS = 0x76

# Các thanh ghi của cảm biến BMP180
BMP180_REGISTER_TEMP = 0x2E
BMP180_REGISTER_PRESSURE = 0x34
BMP180_REGISTER_CONTROL = 0xF4
BMP180_REGISTER_RESULT = 0xF6

# Home Assistant Configuration
HA_URL = os.environ.get("HA_URL", "http://192.168.1.25:8123/api/states/sensor.bmp180_fixed")
HA_TOKEN = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmOTc3ZDExMzA2NDY0MWE3YjhmZDk4ZDJjZWJjMGUyZiIsImlhdCI6MTczMzQ2NTM5MCwiZXhwIjoyMDQ4ODI1MzkwfQ.m0Mz5P3m5wlV5xLjVBS44GubCkJm19foIRlZlcRDbCc")  # Token lấy từ biến môi trường hoặc file cấu hình

# Khởi tạo bus I2C
bus = smbus.SMBus(1)

# Đọc nhiệt độ từ cảm biến
def read_temperature():
    bus.write_byte_data(BMP180_ADDRESS, BMP180_REGISTER_CONTROL, BMP180_REGISTER_TEMP)
    time.sleep(0.005)
    temp_data = bus.read_i2c_block_data(BMP180_ADDRESS, BMP180_REGISTER_RESULT, 2)
    temp = (temp_data[0] << 8) + temp_data[1]
    return temp / 10.0

# Đọc áp suất từ cảm biến
def read_pressure():
    bus.write_byte_data(BMP180_ADDRESS, BMP180_REGISTER_CONTROL, BMP180_REGISTER_PRESSURE)
    time.sleep(0.005)
    press_data = bus.read_i2c_block_data(BMP180_ADDRESS, BMP180_REGISTER_RESULT, 3)
    pressure = (press_data[0] << 16) + (press_data[1] << 8) + press_data[2]
    return pressure / 256.0

# Gửi dữ liệu đến Home Assistant
def send_to_home_assistant(sensor_name, value, unit, friendly_name):
    # URL cho cảm biến cụ thể
    url = f"{HA_URL}/sensor.{sensor_name}"

    # Payload gửi đến Home Assistant
    data = {
        "state": value,
        "attributes": {
            "unit_of_measurement": unit,
            "friendly_name": friendly_name
        }
    }

    # Header chứa token
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    # Gửi dữ liệu
    response = requests.post(url, json=data, headers=headers)

    # Kiểm tra phản hồi
    if response.status_code == 200:
        print(f"Data for {sensor_name} sent successfully!")
    else:
        print(f"Failed to send data for {sensor_name}: {response.status_code} - {response.text}")

# Chương trình chính
if __name__ == "__main__":
    try:
        while True:
            # Đọc dữ liệu từ BMP180
            temperature = read_temperature()
            pressure = read_pressure()

            print(f"Temperature: {temperature}°C")
            print(f"Pressure: {pressure} Pa")

            # Gửi dữ liệu đến Home Assistant
            if HA_TOKEN:
                send_to_home_assistant("bmp180_temperature", temperature, "°C", "BMP180 Temperature")
                send_to_home_assistant("bmp180_pressure", pressure, "Pa", "BMP180 Pressure")
            else:
                print("HA_TOKEN not found. Data will not be sent to Home Assistant.")
            time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
