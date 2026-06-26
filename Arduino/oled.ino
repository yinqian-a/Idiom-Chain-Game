#include <Wire.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_W 128
#define SCREEN_H 64
#define OLED_ADDR 0x3C
#define SDA_PIN 1
#define SCL_PIN 2
#define BTN_PIN 10

Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

String dotBuffer = "";
bool needDraw = false;

// ===================== SETUP =====================
void setup() {
  Serial.begin(115200);
  pinMode(BTN_PIN, INPUT_PULLUP);

  Wire.begin(SDA_PIN, SCL_PIN);
  display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20, 25);
  display.println("Ready");
  display.display();
}

// ===================== 画点阵 =====================
void drawDots(String bits, int w = 64, int h = 16) {
  display.clearDisplay();
  int idx = 0;

  for (int y = 0; y < h; y++) {
    for (int x = 0; x < w; x++) {
      if (bits[idx++] == '1') {
        display.drawPixel(x + 32, y + 24, SSD1306_WHITE);
      }
    }
  }
  display.display();
}

// ===================== 游戏结束 =====================
void showGameOver() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(20, 25);
  display.println("Game Over");
  display.display();
}

// ===================== LOOP =====================
void loop() {
  // ---- 接收串口 ----
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      needDraw = true;
      break;
    }
    dotBuffer += c;
  }

  // ---- 处理命令 ----
  if (needDraw) {
    if (dotBuffer.startsWith("DOT:")) {
      int p1 = dotBuffer.indexOf(':');
      int p2 = dotBuffer.indexOf(':', p1 + 1);
      String data = dotBuffer.substring(p2 + 1);
      drawDots(data, 64, 16);
    }

    if (dotBuffer == "GAMEOVER") {
      showGameOver();
    }

    dotBuffer = "";
    needDraw = false;
  }

  // ---- 按钮结束游戏 ----
  static bool lastBtn = HIGH;
  bool nowBtn = digitalRead(BTN_PIN);
  if (lastBtn == HIGH && nowBtn == LOW) {
    delay(200);
    Serial.println("KEY_PRESS");
  }
  lastBtn = nowBtn;
}