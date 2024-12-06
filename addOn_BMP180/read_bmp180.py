import smbus
import time
import requests

# Địa chỉ I2C của cảm biến BMP180
BMP180_ADDRESS = 0x76

# Các thanh ghi của cảm biến BMP180
BMP180_REGISTER_TEMP = 0x2E
BMP180_REGISTER_PRESSURE = 0x34
BMP180_REGISTER_CONTROL = 0xF4
BMP180_REGISTER_RESULT = 0xF6
BMP180_REGISTER_CALIBRATION = 0xAA

# Khởi tạo bus I2C
bus = smbus.SMBus(5)
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmOTc3ZDExMzA2NDY0MWE3YjhmZDk4ZDJjZWJjMGUyZiIsImlhdCI6MTczMzQ2NTM5MCwiZXhwIjoyMDQ4ODI1MzkwfQ.m0Mz5P3m5wlV5xLjVBS44GubCkJm19foIRlZlcRDbCc"

# Đọc các tham số hiệu chỉnh từ cảm biến
def read_calibration():
    calib = bus.read_i2c_block_data(BMP180_ADDRESS, BMP180_REGISTER_CALIBRATION, 22)
    AC1 = (calib[0] << 8) + calib[1]
    AC2 = (calib[2] << 8) + calib[3]
    AC3 = (calib[4] << 8) + calib[5]
    AC4 = (calib[6] << 8) + calib[7]
    AC5 = (calib[8] << 8) + calib[9]
    AC6 = (calib[10] << 8) + calib[11]
    B1 = (calib[12] << 8) + calib[13]
    B2 = (calib[14] << 8) + calib[15]
    MB = (calib[16] << 8) + calib[17]
    MC = (calib[18] << 8) + calib[19]
    MD = (calib[20] << 8) + calib[21]
    
    return AC1, AC2, AC3, AC4, AC5, AC6, B1, B2, MB, MC, MD

# Đọc nhiệt độ từ cảm biến BMP180
def read_temperature():
    bus.write_byte_data(BMP180_ADDRESS, BMP180_REGISTER_CONTROL, BMP180_REGISTER_TEMP)
    time.sleep(0.005)  # Đảm bảo thời gian ổn định cho cảm biến
    temp_data = bus.read_i2c_block_data(BMP180_ADDRESS, BMP180_REGISTER_RESULT, 2)
    temp_raw = (temp_data[0] << 8) + temp_data[1]
    
    # Đọc các tham số hiệu chỉnh từ cảm biến
    AC1, AC2, AC3, AC4, AC5, AC6, B1, B2, MB, MC, MD = read_calibration()

    # Tính toán nhiệt độ
    X1 = ((temp_raw - AC6) * AC5) >> 15
    X2 = (MC << 11) / (X1 + MD)
    B5 = X1 + X2

    # Đảm bảo B5 là kiểu int trước khi sử dụng toán tử dịch bit
    B5 = int(B5)

    # Tính nhiệt độ theo công thức chuẩn của BMP180
    temperature = (B5 + 8) >> 4  # Tính nhiệt độ theo độ C
    return temperature / 10.0  # Đổi ra độ C

# Đọc áp suất từ cảm biến BMP180
def read_pressure():
    bus.write_byte_data(BMP180_ADDRESS, BMP180_REGISTER_CONTROL, BMP180_REGISTER_PRESSURE)
    time.sleep(0.005)  # Đảm bảo thời gian ổn định cho cảm biến
    press_data = bus.read_i2c_block_data(BMP180_ADDRESS, BMP180_REGISTER_RESULT, 3)
    pressure_raw = (press_data[0] << 16) + (press_data[1] << 8) + press_data[2]
    pressure = pressure_raw / 256.0  # Áp suất theo Pa
    return pressure

# Đẩy dữ liệu lên Home Assistant
def push_to_home_assistant(temperature, pressure):
    url = 'http://192.168.1.25:8123/api/states/sensor.bmp180_temperature'
    headers = {
        'Authorization': f'Bearer {HA_TOKEN}',
        'Content-Type': 'application/json',
    }
    payload = {
        'state': temperature,
        'attributes': {
            'unit_of_measurement': '°C',
            'friendly_name': 'BMP180 Temperature',
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    # Gửi áp suất
    url = 'http://192.168.1.25:8123/api/states/sensor.bmp180_pressure'
    payload = {
        'state': pressure,
        'attributes': {
            'unit_of_measurement': 'Pa',
            'friendly_name': 'BMP180 Pressure',
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Dữ liệu đã được gửi lên Home Assistant.")
    else:
        print(f"Đã có lỗi: {response.status_code} - {response.text}")

if __name__ == '__main__':
    while True:
        temperature = read_temperature()
        pressure = read_pressure()
        print(f"Temperature: {temperature}°C")
        print(f"Pressure: {pressure} Pa")

        # Đẩy dữ liệu lên Home Assistant
        push_to_home_assistant(temperature, pressure)
        
        time.sleep(2)
