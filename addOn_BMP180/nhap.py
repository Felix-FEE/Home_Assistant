from Adafruit_BMP.BMP085 import BMP085

# Khởi tạo cảm biến trên bus 5
sensor = BMP085(busnum=5)

# Đọc giá trị
temperature = sensor.read_temperature()
pressure = sensor.read_pressure()

print(f"Nhiệt độ: {temperature} °C")
print(f"Áp suất: {pressure} Pa")