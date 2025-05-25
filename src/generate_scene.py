from typing import List
from PIL import Image
from content import Chara_animation
from character_setting import Character_type
from setting import default_fps, bg_image_path, default_page_last_pose
from write_title import write_title
from slide_in_text import slide_in_text
from enter_character import enter_character
import os

def generate_scene(
    character_type: Character_type,
    chara_animation: Chara_animation,
    title: List[str],
    contents: List[str],
):
    page_last_pose = default_page_last_pose
    bg_base = Image.open(bg_image_path).convert("RGBA")

    character_intro, bg_with_character = enter_character(
        bg_copy=bg_base,
        character_type=character_type,
        chara_animation=chara_animation,
    )
    title_clip, bg_with_text = write_title(
        intro_clip = character_intro,
        lines = title,
        bg_copy = bg_with_character,
        font_size = 110,
        line_height = 156,
        start_x = 100,
        start_y = 470,
        max_text_width = 880,
    )
    final, b = slide_in_text(
        intro_clip = title_clip,
        lines = contents,
        bg_copy = bg_with_text,
        last_pose=page_last_pose
    )

    os.makedirs("dist", exist_ok=True)

    return final

if __name__ == "__main__":
    final = generate_scene(
        character_type="agree",
        chara_animation="none",
        title=["それって"],
        contents=["ああ", "いい", "ううううううう", "add_asset/maru.png"]
    )
    final.write_videofile("dist/scene_one.mp4", fps=default_fps)