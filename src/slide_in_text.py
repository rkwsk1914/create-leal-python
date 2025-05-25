from typing import List, Union
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from setting import base_duration, font_path, default_page_last_pose
import os

def split_text_by_width(text, font, max_width):
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    return lines

def slide_in_text(
    intro_clip,
    lines: List[Union[str, dict]],
    bg_copy,
    font_size=72,
    line_height=114,
    start_y=660,
    max_text_width=750,
    slide_duration=base_duration,
    final_x=130,
    font_color=(85, 85, 85, 255),
    last_pose=default_page_last_pose
):
    font = ImageFont.truetype(font_path, font_size)
    w, h = bg_copy.size
    clips = [intro_clip]
    final_bg = bg_copy.copy()

    all_lines = []
    for item in lines:
        if isinstance(item, str):
            if item.startswith("add_asset/") and os.path.exists(item):
                all_lines.append({"image": item})
            else:
                all_lines.extend(split_text_by_width(item, font, max_text_width))
        elif isinstance(item, dict) and "image" in item:
            all_lines.append(item)

    for idx, line_item in enumerate(all_lines):
        y = start_y + line_height * idx

        if isinstance(line_item, dict) and "image" in line_item:
            image_path = line_item["image"]
            image = Image.open(image_path).convert("RGBA")
            img_w, img_h = image.size
            image_clip = ImageClip(np.array(image)).set_duration(slide_duration)

            def make_slide_pos(y_offset):
                def slide_pos(t):
                    progress = min(t / slide_duration, 1.0)
                    x = -img_w + progress * (final_x + img_w)
                    return (x, y_offset)
                return slide_pos

            animated_clip = image_clip.set_position(make_slide_pos(y))
            bg_clip = ImageClip(np.array(final_bg)).set_duration(slide_duration)
            composite = CompositeVideoClip([bg_clip, animated_clip], size=(w, h))
            clips.append(composite)

            final_bg.paste(image, (final_x, y), image)

        else:
            line_text = line_item
            text_w = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(line_text, font=font))
            text_img = Image.new("RGBA", (text_w, font_size + 10), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), line_text, font=font, fill=font_color)
            text_np = np.array(text_img)
            text_clip = ImageClip(text_np).set_duration(slide_duration)

            def make_slide_pos(y_offset):
                def slide_pos(t):
                    progress = min(t / slide_duration, 1.0)
                    x = -text_w + progress * (final_x + text_w)
                    return (x, y_offset)
                return slide_pos

            animated_clip = text_clip.set_position(make_slide_pos(y))
            bg_clip = ImageClip(np.array(final_bg)).set_duration(slide_duration)
            composite = CompositeVideoClip([bg_clip, animated_clip], size=(w, h))
            clips.append(composite)

            draw_final = ImageDraw.Draw(final_bg)
            draw_final.text((final_x, y), line_text, font=font, fill=font_color)

    # ✅ 最終状態で止める
    final_np = np.array(final_bg)
    final_clip = ImageClip(final_np).set_duration(last_pose)
    clips.append(final_clip)

    return concatenate_videoclips(clips, method="compose"), final_bg