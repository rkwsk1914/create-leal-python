from typing import List
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from setting import base_duration, font_path

duration_per_char = 0.1
underline_anim_duration = base_duration
final_pause_duration = base_duration

pencil_path = "asset/pencil.png"

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

def write_title(
    intro_clip,
    lines: List[str],
    bg_copy,
    font_size=160,
    line_height=220,
    start_x=100,
    start_y=506,
    max_text_width=800,
    underline_color = (251, 141, 141, int(255 * 100)),
    font_color = (85, 85, 85, 255),
    last_pose = 0.2
):
    font = ImageFont.truetype(font_path, font_size)
    w, h = bg_copy.size
    clips = [intro_clip]
    prev_line_states = []
    line_offset = 0
    line_total = sum(len(split_text_by_width(l, font, max_text_width)) for l in lines)
    current_line_num = 0

    for logical_line in lines:
        wrapped_lines = split_text_by_width(logical_line, font, max_text_width)

        for line_text in wrapped_lines:
            current_line_num += 1

            for i in range(len(line_text) + 1):
                bg = bg_copy.copy()
                for img in prev_line_states:
                    bg = Image.alpha_composite(bg, img)

                draw = ImageDraw.Draw(bg)
                y = start_y + line_height * line_offset
                visible_text = line_text[:i]
                text_width = draw.textlength(visible_text, font=font)
                draw.text((start_x, y), visible_text, font=font, fill=font_color)

                bg_np = np.array(bg)
                bg_clip = ImageClip(bg_np)

                if i == 0:
                    composite = bg_clip.set_duration(duration_per_char)
                elif i < len(line_text):
                    pencil_x = start_x + text_width
                    pencil_y = y - (font_size / 2)
                    pencil_clip = ImageClip(pencil_path).set_position((pencil_x, pencil_y)).set_duration(duration_per_char)
                    composite = CompositeVideoClip([bg_clip.set_duration(duration_per_char), pencil_clip], size=(w, h))
                else:
                    underline_y = y + font_size + 10
                    full_text_width = draw.textlength(line_text, font=font)
                    n_frames = int(underline_anim_duration / duration_per_char)

                    underline_img = None
                    for j in range(1, n_frames + 1):
                        underline_img = bg.copy()
                        underline_draw = ImageDraw.Draw(underline_img)
                        curr_width = int(full_text_width * j / n_frames)
                        underline_draw.rectangle(
                            [start_x, underline_y, start_x + curr_width, underline_y + 30],
                            fill=underline_color
                        )
                        u_np = np.array(underline_img)
                        u_clip = ImageClip(u_np).set_duration(duration_per_char)
                        clips.append(u_clip)

                    final_np = np.array(underline_img)
                    final_duration = final_pause_duration if current_line_num == line_total else 0.01
                    final_clip = ImageClip(final_np).set_duration(final_duration)
                    clips.append(final_clip)

                    if current_line_num == line_total:
                        hold_clip = ImageClip(final_np).set_duration(last_pose)
                        clips.append(hold_clip)

                    prev_line_states.append(underline_img.copy())

                    # ✅ 最終状態の背景画像を保持
                    bg_with_text = underline_img.copy()
                    break

                clips.append(composite)

            line_offset += 1

    final = concatenate_videoclips(clips, method="compose")
    return final, bg_with_text  # ✅ アニメーション + 最終状態の背景画像