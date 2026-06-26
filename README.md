## README.md


# 成语接龙游戏 — OCR视觉识别 + ESP32硬件联动

基于 PaddleOCR 和 ESP32-S3 的成语接龙游戏，PC端通过 OCR 自动识别用户在记事本中输入的成语，ESP32 驱动 OLED 屏幕实时同步显示当前成语，外接按键一键结束游戏。

## 项目简介

传统成语接龙游戏需要用户在游戏界面内打字输入，交互方式单一。本项目将输入行为迁移至外部文本编辑器（如记事本），程序通过定时截图 + OCR 自动捕获用户输入的成语并判断接龙合法性，同时通过串口将点阵数据推送至 ESP32 驱动的 OLED 屏幕实时显示，实现 PC 端与硬件端的软硬联动。

## 功能特点

- **OCR 自动识别**：用户在记事本中书写成语，程序每 2 秒自动截图识别，无需手动输入
- **智能接龙判断**：自动校验成语是否在库中、首尾字是否匹配，正确接龙 +10 分
- **硬件同步显示**：ESP32 + OLED 实时同步显示当前成语，游戏状态从屏幕延伸至桌面
- **一键结束游戏**：ESP32 外接按键或 PC 端按钮均可结束游戏
- **防误识别机制**：截图涂黑游戏窗口区域 + UI 文字黑名单过滤，有效避免界面文字干扰
- **点阵显示**：成语转换为 16×64 点阵数据在 OLED 上绘制，清晰且具有复古电子屏风格
- **成语库可扩展**：支持外部 `成语.txt` 文件，每行一个成语，用户可按需增删

## 系统架构


PC 端 (Python)
├── Tkinter 界面（当前成语、得分、日志、控制按钮）
├── PaddleOCR 识别（截图 + 涂黑屏蔽 + OCR 提取）
├── 成语接龙逻辑（状态管理、合法性校验、得分更新）
├── 点阵生成（PIL 渲染成语 → 二值化 → 编码）
└── 串口通信（发送点阵数据、接收按键事件）
        │
        ▼ USB 串口
ESP32-S3 硬件端
├── OLED 显示（SSD1306，128×64，I2C 接口）
├── 点阵解析与绘制
└── 按键检测（GPIO10，下降沿触发）


## 硬件清单

| 硬件 | 型号/规格 | 数量 |
|------|----------|------|
| ESP32-S3 开发板 | ESP32-S3 Dev Module | 1 |
| OLED 显示屏 | SSD1306，128×64，I2C接口 | 1 |
| 按键 | 轻触开关 | 1 |
| 杜邦线 | 母对母 | 若干 |
| USB 数据线 | Type-C | 1 |

### 硬件接线

| OLED 引脚 | ESP32-S3 引脚 |
|----------|--------------|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO1 |
| SCL | GPIO2 |

| 按键引脚 | ESP32-S3 引脚 |
|----------|--------------|
| 一端 | GPIO10 |
| 另一端 | GND |

## 软件依赖

### Python 环境
- Python 3.9+
- 虚拟环境（推荐）

### 依赖库

```bash
pip install paddlepaddle==2.6.2
pip install paddleocr==2.8.1
pip install pyautogui
pip install pillow
pip install pyserial
```

或使用 `requirements.txt` 一键安装：
```
pip install -r requirements.txt
```

### ESP32 开发环境
- Arduino IDE 2.x
- 开发板：ESP32S3 Dev Module
- USB CDC On Boot：Enabled
- USB Mode：USB-OTG (TinyUSB)

### 库依赖（Arduino）
- Adafruit SSD1306
- Adafruit GFX

## 目录结构

```
PyChengyu/
├── main.py              # PC 端主程序（UI + OCR + 逻辑）
├── config.py            # 配置文件（串口号、波特率、字体路径）
├── dot_gen.py           # 点阵生成模块（成语 → 点阵字符串）
├── utils.py             # 工具函数（成语库加载）
├── oled.ino             # ESP32 固件源码
├── 成语.txt              # 成语库（每行一个成语）
├── requirements.txt     # Python 依赖列表
└── README.md            # 本文件
```

## 使用说明

### 1. 准备成语库
使用项目已有的`成语.txt`

### 2. 烧录 ESP32 固件
1. 用 Arduino IDE 打开 `oled.ino`
2. 工具 → 开发板 → ESP32S3 Dev Module
3. 工具 → 端口 → 选择 ESP32 的 COM 口
4. 点击上传按钮

### 3. 运行 PC 端程序
```bash
python main.py
```

### 4. 开始游戏
1. 打开记事本，放在屏幕**右侧**（不要遮挡游戏窗口）
2. 游戏窗口显示当前成语和提示（如「需要以「意」开头」）
3. 在记事本中输入对应的成语，保存即可
4. 程序每 2 秒自动识别一次，接龙正确则自动更新并 +10 分
5. 按 ESP32 外接按键或点击「结束游戏」退出

## 测试结果

| 测试项 | 结果 |
|--------|------|
| OCR 识别准确率（16号字体以上） | 98.75% |
| 串口通信成功率（50次连续刷新） | 100% |
| 点阵显示清晰度 | 高（含复杂笔画汉字） |
| 端到端功能联调 | 6/6 通过 |


## 常见问题

**Q：OCR 识别不到成语？**  
A：确保记事本字体 ≥ 16号，背景为白色，文字为黑色。游戏窗口涂黑区域会屏蔽界面文字，不会干扰识别。

**Q：ESP32 连接失败？**  
A：检查 `config.py` 中的 `PORT` 是否为实际串口号；确认 USB CDC On Boot 已启用；按下 BOOT 键再插 USB 进入下载模式。

**Q：OLED 不显示？**  
A：检查 I2C 接线是否正确（SDA→GPIO1，SCL→GPIO2）；确认 OLED 地址是否为 0x3C；检查供电（3.3V）。

**Q：点阵显示模糊？**  
A：检查 `dot_gen.py` 中的 `FONT_PATH` 是否指向有效的字体文件；尝试调整字号。

## 后续改进方向

- 增加图像预处理（灰度化、二值化）提升 OCR 识别率
- 支持基于屏幕变化检测的动态触发，降低 CPU 占用
- OLED 升级为彩色屏，增加正确/错误视觉反馈
- 接入成语释义数据库，提供学习功能
- 局域网多人联机模式

## 许可证

MIT License

## 致谢

本项目基于以下开源项目构建：
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [pyautogui](https://github.com/asweigart/pyautogui)
- [Adafruit_SSD1306](https://github.com/adafruit/Adafruit_SSD1306)

## 作者

本项目为课程设计/毕业设计作品，仅供学习交流使用。

---

**年份**：2026
