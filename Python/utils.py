import os
import re

def load_idioms(path="成语.txt"):
    idioms = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().split()[0]
                if len(word) == 4 and re.match(r"^[\u4e00-\u9fff]{4}$", word):
                    idioms.append(word)
    except Exception as e:
        print("❌ 成语库加载失败:", e)
    return idioms