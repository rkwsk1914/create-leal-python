from typing import List
from PIL import Image
from setting import default_fps, bg_image_path, default_page_last_pose
from content import Chara_animation
from character_setting import Character_type
from write_title import write_title
from enter_character import enter_character
import os

def generate_scene_top(
    character_type: Character_type,
    chara_animation: Chara_animation,
    title: List[str]
):
    page_last_pose = default_page_last_pose
    bg_base = Image.open(bg_image_path).convert("RGBA")

    character_intro, bg_with_character = enter_character(
        bg_copy=bg_base,
        character_type=character_type,
        chara_animation=chara_animation,
    )
    final, _ ,_ = write_title(
        intro_clip = character_intro,
        lines = title,
        bg_copy = bg_with_character,
        font_size = 128,
        line_height = 220,
        start_x = 100,
        start_y = 506,
        max_text_width = 800,
        last_pose=page_last_pose
    )

    os.makedirs("dist", exist_ok=True)

    return final

if __name__ == "__main__":
    final = generate_scene_top(
        character_type="surprised",
        chara_animation="jump",
        title=[
            "それって",
            "タンパク質",
            "不足かも！"
        ]
    )
    final.write_videofile("dist/scene_top.mp4", fps=default_fps)