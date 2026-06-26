from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH, FONT_SIZE

def idiom_to_dot(idiom):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    img = Image.new("1", (FONT_SIZE * 4, FONT_SIZE), 0)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), idiom, font=font, fill=1)

    bits = []
    for y in range(FONT_SIZE):
        for x in range(FONT_SIZE * 4):
            bits.append("1" if img.getpixel((x, y)) else "0")
    return "".join(bits)