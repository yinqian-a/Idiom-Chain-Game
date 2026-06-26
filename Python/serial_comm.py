import serial
import time
from config import PORT, BAUD

class SerialComm:
    def __init__(self):
        self.ser = None
        try:
            self.ser = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
            print("✅ ESP32 已连接")
        except Exception as e:
            print("⚠️ 未连接 ESP32:", e)

    def send_dot(self, dots):
        if self.ser:
            self.ser.write(f"DOT:{len(dots)}:{dots}\n".encode())

    def send_gameover(self):
        if self.ser:
            self.ser.write(b"GAMEOVER\n")

    def close(self):
        if self.ser:
            self.ser.close()