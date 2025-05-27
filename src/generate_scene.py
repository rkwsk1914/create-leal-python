from typing import List
from PIL import Image
import os

from content import Chara_animation
from character_setting import Character_type
from setting import (
    default_fps,
    bg_image_path,
    default_page_last_pose,
    note_line_heigh,
)

from add_label_overlay import add_label_overlay
from write_title import write_title
from slide_in_text import slide_in_text
from enter_character import enter_character

def generate_scene(
    character_type: Character_type,
    chara_animation: Chara_animation,
    title: List[str],
    contents: List[str],
    leal_title: List[str],
    leal_number,
    with_animation=True,
):
    page_last_pose = default_page_last_pose
    bg_base = Image.open(bg_image_path).convert("RGBA")

    bg_base = add_label_overlay(bg_base, leal_title=leal_title, leal_number=leal_number)

    if not with_animation:
        chara_animation = "none"

    character_intro, bg_with_character = enter_character(
        bg_copy=bg_base,
        character_type=character_type,
        chara_animation=chara_animation,
    )

    title_clip, bg_with_text, title_end_y = write_title(
        intro_clip=character_intro,
        lines=title,
        bg_copy=bg_with_character,
        font_size=72,
        line_height=114,
        start_x=100,
        start_y=470,
        max_text_width=880,
        with_animation=with_animation,
    )

    # 💡 Y座標で narrow_after_lines の判定を動的に行う
    max_text_width = 880
    font_size = 54
    adjusted_start_y = 660
    narrow_check_point_y = 697

    #print(f"[DEBUG] title_end_y = {title_end_y}")
    #print(f"[DEBUG] narrow_check_point_y = {narrow_check_point_y}")

    if title_end_y >= narrow_check_point_y:
        adjusted_start_y = 660 + note_line_heigh + 2

    final, _ = slide_in_text(
        intro_clip=title_clip,
        lines=contents,
        bg_copy=bg_with_text,
        start_y=adjusted_start_y,
        max_text_width=max_text_width,
        font_size=font_size,
        last_pose=page_last_pose,
        with_animation=with_animation,
    )

    os.makedirs("dist", exist_ok=True)
    return final

if __name__ == "__main__":
    final = generate_scene(
        character_type="agree",
        chara_animation="none",
        leal_number="#02",
        leal_title=[
            "それって",
            "タンパク質",
            "不足かも！"
        ],
        title=["体内の電気は“自家発電”！？"],
        contents=[
            "心臓は自律神経と電気信号で24時間動き続けてる！",
            "僕たちの体にも微弱な電気があって、心臓もその**電気信号**で動いてるんだ！ああああああああああああああああああああああああああいいいいい",
            "🚨緊急時に使うAEDも、電気ショックで心臓を再始動させる装置！",
            # {"image": "add_asset/maru.png"},
        ]
        # title=["ああああああああああああああああ"],
        # contents=[
        #     "ああああああああああああああああああああああああああああああああああああああああああああ",
        #     "あああああああああああ**あああああああああああああ**ああああああああああああああああああああ",
        #     "ああああああああああああああああああああああああああああああああああああああああああああああ",
        #     # {"image": "add_asset/maru.png"},
        # ]
    )
    final.write_videofile("check/scene_one.mp4", fps=default_fps)