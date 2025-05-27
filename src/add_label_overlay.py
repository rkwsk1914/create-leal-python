# src/add_label_overlay.py
from PIL import ImageDraw, ImageFont
from moviepy.editor import ImageClip
import numpy as np
from setting import font_path

def add_label_overlay(
    bg_image,
    leal_number,
    leal_title=None,
    leal_number_font_size=72,
    leal_title_font_size=40,
    position=(100, 205),
    font_color=(85, 85, 85, 255),
):
    """
    背景画像にラベル文字（leal_number だけ または leal_number - leal_title_str -）を合成して返す（PIL.Image）
    """
    bg = bg_image.copy()
    draw = ImageDraw.Draw(bg)

    font_number = ImageFont.truetype(font_path, leal_number_font_size)
    font_title = ImageFont.truetype(font_path, leal_title_font_size)

    x, y = position

    if leal_title:
        leal_title_str = "".join(leal_title)
        leal_title_str_y = 230

        # leal_number
        draw.text((x, y), leal_number, font=font_number, fill=font_color)
        number_width = draw.textlength(leal_number, font=font_number)

        # " - "
        hyphen1 = " - "
        hyphen1_width = draw.textlength(hyphen1, font=font_title)
        draw.text((x + number_width, leal_title_str_y), hyphen1, font=font_title, fill=font_color)

        # leal_title_str
        title_x = x + number_width + hyphen1_width
        draw.text((title_x, leal_title_str_y), leal_title_str, font=font_title, fill=font_color)
        title_width = draw.textlength(leal_title_str, font=font_title)

        # " -"
        hyphen2 = " -"
        draw.text((title_x + title_width, leal_title_str_y), hyphen2, font=font_title, fill=font_color)
    else:
        # leal_number のみ表示
        draw.text((x, y), leal_number, font=font_number, fill=font_color)

    return bg