import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips

from setting import base_duration, default_page_last_pose, font_path

def parse_underlined_segments(text: str):
    """テキストから強調（下線）部分を抽出"""
    pattern = re.compile(r'\*\*(.+?)\*\*')
    result = []
    last_end = 0
    for match in pattern.finditer(text):
        if last_end < match.start():
            result.append((text[last_end:match.start()], False))
        result.append((match.group(1), True))
        last_end = match.end()
    if last_end < len(text):
        result.append((text[last_end:], False))
    return result

def split_segments_by_width(segments, font, max_width):
    """セグメントを max_width に合わせて改行"""
    lines = []
    current_line = []
    current_width = 0
    for text, underline in segments:
        for char in text:
            w = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(char, font=font)
            if current_width + w > max_width and current_line:
                lines.append(current_line)
                current_line = []
                current_width = 0
            current_line.append((char, underline))
            current_width += w
    if current_line:
        lines.append(current_line)
    return lines

def slide_in_text(
    intro_clip,
    lines,
    bg_copy,
    font_size=72,
    line_height=114,
    start_y=660,
    max_text_width=750,
    slide_duration=base_duration,
    final_x=130,
    font_color=(85, 85, 85, 255),
    last_pose=default_page_last_pose,
    underline_fill=(251, 141, 141, 255),
    underline_width=20,
    underline_anim_duration=0.03,
    underline_frame_duration=0.03
):
    font = ImageFont.truetype(font_path, font_size)
    w, h = bg_copy.size
    clips = [intro_clip]
    final_bg = bg_copy.copy()
    line_offset = 0

    # 下線情報を溜めておく
    underline_infos = []

    for item in lines:
        if isinstance(item, str):
            segments = parse_underlined_segments(item)
            wrapped_lines = split_segments_by_width(segments, font, max_text_width)

            for line in wrapped_lines:
                y = start_y + line_height * line_offset

                # テキスト画像の描画
                text_img = Image.new("RGBA", (w, font_size + 20), (0, 0, 0, 0))
                draw = ImageDraw.Draw(text_img)

                x_cursor = final_x
                line_underlines = []

                for char, underline in line:
                    draw.text((x_cursor, 0), char, font=font, fill=font_color)
                    char_width = draw.textlength(char, font=font)
                    if underline:
                        line_underlines.append((x_cursor, x_cursor + char_width, y + font_size + 5))
                    x_cursor += char_width

                text_np = np.array(text_img)
                text_clip = ImageClip(text_np).set_duration(slide_duration)

                def slide_pos_gen(y_pos, clip_w=text_img.width):
                    def slide_pos(t):
                        progress = min(t / slide_duration, 1.0)
                        x = -clip_w + progress * (final_x + clip_w)
                        return (x, y_pos)
                    return slide_pos

                animated_clip = text_clip.set_position(slide_pos_gen(y))
                bg_clip = ImageClip(np.array(final_bg)).set_duration(slide_duration)
                composite = CompositeVideoClip([bg_clip, animated_clip], size=(w, h))
                clips.append(composite)

                # 背景に描き込み
                draw_final = ImageDraw.Draw(final_bg)
                x_cursor = final_x
                for char, underline in line:
                    draw_final.text((x_cursor, y), char, font=font, fill=font_color)
                    char_width = draw_final.textlength(char, font=font)
                    x_cursor += char_width

                if line_underlines:
                    underline_infos.append({
                        "positions": line_underlines,
                        "y": y + font_size + 5
                    })

                line_offset += 1

        elif isinstance(item, dict) and "image" in item:
            image_path = item["image"]
            image = Image.open(image_path).convert("RGBA")
            img_w, img_h = image.size
            y = start_y + line_height * line_offset

            image_clip = ImageClip(np.array(image)).set_duration(slide_duration)

            def slide_pos_image(t):
                progress = min(t / slide_duration, 1.0)
                x = -img_w + progress * (final_x + img_w)
                return (x, y)

            animated_clip = image_clip.set_position(slide_pos_image)
            bg_clip = ImageClip(np.array(final_bg)).set_duration(slide_duration)
            composite = CompositeVideoClip([bg_clip, animated_clip], size=(w, h))
            clips.append(composite)

            # 背景に描き込み
            final_bg.paste(image, (final_x, y), image)
            line_offset += 1

    # 下線アニメーションを追加
    for info in underline_infos:
        y = info["y"]
        positions = info["positions"]

        for start_x, end_x, y_pos in positions:
            width = end_x - start_x
            frames = int(underline_anim_duration / underline_frame_duration)

            for i in range(1, frames + 1):
                underline_img = final_bg.copy()
                draw = ImageDraw.Draw(underline_img)
                current_width = int(width * (i / frames))
                draw.rectangle(
                    [start_x, y_pos, start_x + current_width, y_pos + underline_width],
                    fill=underline_fill
                )
                clip = ImageClip(np.array(underline_img)).set_duration(underline_frame_duration)
                clips.append(clip)

            # 最終保持
            final_img = final_bg.copy()
            draw = ImageDraw.Draw(final_img)
            draw.rectangle([start_x, y, end_x, y + underline_width], fill=underline_fill)
            final_bg = final_img.copy()

    final_clip = ImageClip(np.array(final_bg)).set_duration(last_pose)
    clips.append(final_clip)

    return concatenate_videoclips(clips, method="compose"), final_bg