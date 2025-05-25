from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np
from setting import base_duration, default_fps
from write_title import write_title

fps=default_fps

def jump_in_character(
    bg_copy,
    character_path = "asset/me/surprised.png",
    character_left = 50,
    character_bottom = 334,
):
    w, h = bg_copy.size
    character_img = Image.open(character_path)
    character_clip_raw = ImageClip(np.array(character_img)).set_duration(1.0)
    character_w, character_h = character_img.size

    # キャラ登場用背景を生成（最背面）
    bg_with_character = bg_copy.copy()
    bg_with_character.paste(
        character_img,
        (w -character_left - character_w, h - character_bottom - character_h),
        character_img
    )

    # ========= スライドイン + ジャンプ位置関数 =========
    # ① スライドイン：下から上に移動（最初の0.5秒）
    # ② ジャンプ：バウンド（次の0.5秒）
    slide_in_duration = base_duration
    jump_duration = base_duration
    total_intro_duration = slide_in_duration + jump_duration
    final_y = h - character_bottom - character_h  # 最終着地位置
    jump_height = 100

    def slide_and_jump_position(t):
        if t < slide_in_duration:
            # スライドイン：一定速度で下から上
            start_y = h + 200
            y = start_y + (final_y - start_y) * (t / slide_in_duration)
        else:
            # ジャンプ：sinカーブでバウンド
            t2 = t - slide_in_duration
            bounce = np.sin(t2 / jump_duration * np.pi)
            y = final_y - bounce * jump_height
        x = w - character_left - character_w
        return (x, y)

    character_intro_clip = (
        character_clip_raw.set_position(slide_and_jump_position)
        .set_duration(total_intro_duration)
        #.fadein(slide_in_duration)
    )
    bg_clip = ImageClip(np.array(bg_copy)).set_duration(total_intro_duration)
    character_intro = CompositeVideoClip([bg_clip, character_intro_clip], size=(w, h)).set_fps(fps)

    return character_intro, bg_with_character