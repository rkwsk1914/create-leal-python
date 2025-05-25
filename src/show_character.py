from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np
from setting import base_duration, default_fps

fps = default_fps

def show_character(
    bg_copy,
    character_path = "asset/me/surprised.png",
    character_left = 50,
    character_bottom = 334,
):
    w, h = bg_copy.size
    character_img = Image.open(character_path)
    character_w, character_h = character_img.size

    # キャラ登場用背景を生成
    bg_with_character = bg_copy.copy()
    bg_with_character.paste(
        character_img,
        (w - character_left - character_w, h - character_bottom - character_h),
        character_img
    )

    # キャラを固定位置に表示
    character_clip = (
        ImageClip(np.array(character_img))
        .set_duration(base_duration)
        .set_position((w - character_left - character_w, h - character_bottom - character_h))
    )

    bg_clip = ImageClip(np.array(bg_copy)).set_duration(base_duration)
    character_intro = CompositeVideoClip([bg_clip, character_clip], size=(w, h)).set_fps(fps)

    return character_intro, bg_with_character