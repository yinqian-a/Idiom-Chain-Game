import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import serial
import threading
import time
import queue
import os
import re
from datetime import datetime
from paddleocr import PaddleOCR
import pyautogui
from PIL import Image, ImageDraw

# ================== 配置 ==================
PORT = "COM5"
BAUD = 115200
IDIOM_FILE = "成语.txt"

# ================== 主类 ==================
class IdiomGameOCR:
    def __init__(self):
        # 1️⃣ 窗口（必须最先）
        self.root = tk.Tk()
        self.root.title("成语接龙游戏")
        self.root.geometry("500x750+30+50")
        self.root.configure(bg="#F5F5F0")

        # 2️⃣ 状态变量
        self.ser = None
        self.reader = None
        self.idioms = []
        self.current_idiom = ""
        self.score = 0
        self.game_running = False

        # 3️⃣ UI
        self.setup_ui()

        # 4️⃣ 后台初始化
        threading.Thread(target=self.background_init, daemon=True).start()

        # 5️⃣ 主循环
        self.root.mainloop()

    # ================== UI ==================
    def setup_ui(self):
        tk.Label(self.root, text="成语接龙",
                 font=("Microsoft YaHei", 24, "bold"),
                 bg="#F5F5F0").pack(pady=15)

        self.status_label = tk.Label(
            self.root, text="初始化中...",
            font=("Microsoft YaHei", 14),
            bg="#F5F5F0"
        )
        self.status_label.pack()

        self.idiom_label = tk.Label(
            self.root, text="",
            font=("Microsoft YaHei", 32, "bold"),
            bg="#F5F5F0"
        )
        self.idiom_label.pack(pady=10)

        self.score_label = tk.Label(
            self.root, text="0 分",
            font=("Microsoft YaHei", 16),
            bg="#F5F5F0"
        )
        self.score_label.pack()

        self.log = scrolledtext.ScrolledText(
            self.root, width=60, height=15,
            font=("Consolas", 10)
        )
        self.log.pack(padx=10, pady=10)

        btn_frame = tk.Frame(self.root, bg="#F5F5F0")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="刷新成语",
                  command=self.refresh_idiom).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="手动识别",
                  command=self.manual_ocr).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="结束游戏",
                  command=self.end_game).pack(side=tk.LEFT, padx=5)

    # ================== 初始化 ==================
    def background_init(self):
        try:
            self.log_message("📖 加载成语库...")
            self.load_idioms()

            self.log_message("🤖 初始化 OCR...")
            os.environ['PPOCR_LOG_LEVEL'] = 'ERROR'
            self.reader = PaddleOCR(lang='ch')

            self.log_message("🔌 连接 ESP32...")
            self.ser = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
            self.log_message("✅ ESP32 已连接")

            self.current_idiom = random.choice(self.idioms)
            self.game_running = True

            self.root.after(0, self.on_ready)
        except Exception as e:
            self.log_message(f"❌ 初始化失败: {e}")

    def on_ready(self):
        self.status_label.config(text="准备就绪")
        self.idiom_label.config(text=self.current_idiom)
        self.send_to_esp32()

        threading.Thread(target=self.ocr_loop, daemon=True).start()
        threading.Thread(target=self.esp_listener, daemon=True).start()

    # ================== 成语库 ==================
    def load_idioms(self):
        if not os.path.exists(IDIOM_FILE):
            self.idioms = ["一帆风顺", "二话不说", "三心二意", "四海为家"]
            return

        with open(IDIOM_FILE, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().split()[0]
                if len(w) == 4 and re.match(r"^[\u4e00-\u9fff]{4}$", w):
                    self.idioms.append(w)

    # ================== OCR ==================
    def ocr_loop(self):
        while self.game_running:
            idiom = self.capture_and_ocr()
            if idiom:
                self.process_idiom(idiom)
            time.sleep(2)

    def capture_and_ocr(self):
        img = pyautogui.screenshot()
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 480, 720), fill=(0, 0, 0))
        img.save("temp.png")

        res = self.reader.ocr("temp.png")
        if not res or not res[0]:
            return None

        for line in res[0]:
            t = line[1][0]
            if self.is_valid_idiom(t):  # ✅ 回归
                return t
        return None

    def is_valid_idiom(self, text):
        """
        ✅ 终极防火墙
        专门针对当前 UI 界面定制
        """
        if not text or len(text) != 4:
            return False

        # 1️⃣ 必须是纯中文（禁止英文、数字、符号）
        if not re.fullmatch(r'^[\u4e00-\u9fff]{4}$', text):
            return False

        # 2️⃣ 终极黑名单（根据你的 UI 逐字核对）
        blacklist = [
            # 标题栏
            "成语接龙", "游戏", "准备就绪", "初始化中", "初始化",

            # 按钮文字
            "刷新成语", "手动识别", "结束游戏", "刷新", "识别", "结束",

            # 日志里可能出现的词
            "加载", "成语库", "成功", "连接", "已连接", "发送", "失败",
            "PaddleOCR", "OCR", "AI", "Python", "IDIOM", "KEY", "PRESS",

            # 分数
            "分",

            # 防止识别到提示语
            "需要以", "开头", "当前", "记录", "日志",
            "编辑查看","毕设模板","按钮文字","百度网盘","阅读全部"
        ]

        for word in blacklist:
            if word in text:
                # 一旦发现黑名单里的词，直接判死刑
                return False

        return True

    # ================== 游戏逻辑 ==================
    def process_idiom(self, idiom):
        if idiom == self.current_idiom:
            return

        if idiom not in self.idioms:
            self.log_message(f"❌ {idiom} 不在成语库")
            return

        if idiom[0] == self.current_idiom[-1]:
            self.score += 10
            self.score_label.config(text=f"{self.score} 分")
            self.log_message(f"✅ {self.current_idiom} → {idiom}")

            self.current_idiom = idiom
            self.idiom_label.config(text=idiom)
            self.send_to_esp32()
        else:
            self.log_message(f"❌ 应以「{self.current_idiom[-1]}」开头")

    # ================== ESP32 ==================
    def send_to_esp32(self):
        if not self.ser:
            return
        try:
            from dot_gen import idiom_to_dot
            dots = idiom_to_dot(self.current_idiom)
            self.ser.write(f"DOT:{len(dots)}:{dots}\n".encode())
            self.log_message(f"📡 已发送到 ESP32: {self.current_idiom}")
        except Exception as e:
            self.log_message(f"⚠️ ESP32 发送失败: {e}")

    def esp_listener(self):
        while self.game_running and self.ser:
            if self.ser.in_waiting:
                if self.ser.readline().decode().strip() == "KEY_PRESS":
                    self.root.after(0, self.end_game)
            time.sleep(0.05)

    # ================== 工具 ==================
    def refresh_idiom(self):
        self.current_idiom = random.choice(self.idioms)
        self.idiom_label.config(text=self.current_idiom)
        self.send_to_esp32()

    def manual_ocr(self):
        idiom = self.capture_and_ocr()
        if idiom:
            self.process_idiom(idiom)

    def log_message(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, lambda: self.log.insert(tk.END, f"[{ts}] {msg}\n"))
        self.root.after(0, lambda: self.log.see(tk.END))

    def end_game(self):
        self.game_running = False
        if self.ser:
            self.ser.write(b"GAMEOVER\n")
            self.ser.close()
        self.root.quit()

# ================== 入口 ==================
if __name__ == "__main__":
    IdiomGameOCR()