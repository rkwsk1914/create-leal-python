import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from setting import base_duration, default_page_last_pose, font_path, note_line_heigh

def parse_underlined_segments(text: str):
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
    font_size=54,
    line_height=note_line_heigh,
    start_y=660,
    max_text_width=880,
    max_text_width_narrow=700,
    narrow_threshold_y=1113,
    slide_duration=base_duration,
    final_x=100,
    font_color=(85, 85, 85, 255),
    last_pose=default_page_last_pose,
    underline_fill=(254, 171, 36, 255),
    underline_width=20,
    underline_anim_duration=0.03,
    underline_frame_duration=0.03,
    underline_offset_y=12,
    with_animation=True
):
    font = ImageFont.truetype(font_path, font_size)
    w, h = bg_copy.size
    clips = [intro_clip] if with_animation else []
    final_bg = bg_copy.copy()
    line_offset = 0
    underline_infos = []

    for item in lines:
        if isinstance(item, str):
            segments = parse_underlined_segments(item)
            current_max_width = max_text_width
            wrapped_lines = split_segments_by_width(segments, font, current_max_width)

            estimated_total_y = start_y + line_offset * line_height + len(wrapped_lines) * line_height
            if estimated_total_y >= narrow_threshold_y:
                current_max_width = max_text_width_narrow
                wrapped_lines = split_segments_by_width(segments, font, current_max_width)

            for line in wrapped_lines:
                y = start_y + line_offset * line_height
                line_underlines = []

                text_img = Image.new("RGBA", (w, font_size + 20), (0, 0, 0, 0))
                draw = ImageDraw.Draw(text_img)
                x_cursor = final_x
                for char, underline in line:
                    draw.text((x_cursor, 0), char, font=font, fill=font_color)
                    char_width = draw.textlength(char, font=font)
                    if underline:
                        line_underlines.append((x_cursor, x_cursor + char_width, y))
                    x_cursor += char_width

                if with_animation:
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
                    clips.append(CompositeVideoClip([bg_clip, animated_clip], size=(w, h)))

                # 背景に文字描画（常に行う）
                draw_final = ImageDraw.Draw(final_bg)
                x_cursor = final_x
                for char, underline in line:
                    draw_final.text((x_cursor, y), char, font=font, fill=font_color)
                    char_width = draw_final.textlength(char, font=font)
                    x_cursor += char_width

                if line_underlines:
                    underline_infos.append({
                        "positions": [(x0, x1, y + font_size + 5) for x0, x1, y in line_underlines],
                        "y": y + font_size + 5
                    })

                line_offset += 1

        elif isinstance(item, dict) and "image" in item:
            image = Image.open(item["image"]).convert("RGBA")
            img_w, img_h = image.size
            y = start_y + line_offset * line_height
            final_bg.paste(image, (final_x, y), image)

            if with_animation:
                image_clip = ImageClip(np.array(image)).set_duration(slide_duration)

                def slide_pos_image(t):
                    progress = min(t / slide_duration, 1.0)
                    x = -img_w + progress * (final_x + img_w)
                    return (x, y)

                animated_clip = image_clip.set_position(slide_pos_image)
                bg_clip = ImageClip(np.array(final_bg)).set_duration(slide_duration)
                clips.append(CompositeVideoClip([bg_clip, animated_clip], size=(w, h)))

            line_offset += 1

    # ✅ 下線アニメーション または 静的描画
    for info in underline_infos:
        for start_x, end_x, y_pos in info["positions"]:
            width = end_x - start_x
            underline_y = y_pos + underline_offset_y

            if with_animation:
                frames = int(underline_anim_duration / underline_frame_duration)
                for i in range(1, frames + 1):
                    underline_img = final_bg.copy()
                    draw = ImageDraw.Draw(underline_img)
                    curr_width = int(width * (i / frames))
                    draw.line(
                        [(start_x, underline_y), (start_x + curr_width, underline_y)],
                        fill=underline_fill,
                        width=underline_width
                    )
                    clips.append(ImageClip(np.array(underline_img)).set_duration(underline_frame_duration))

            # 最終状態の下線は常に描画
            draw_final = ImageDraw.Draw(final_bg)
            draw_final.line(
                [(start_x, underline_y), (start_x + width, underline_y)],
                fill=underline_fill,
                width=underline_width
            )

    # ✅ 最終状態保持
    clips.append(ImageClip(np.array(final_bg)).set_duration(last_pose))
    return concatenate_videoclips(clips, method="compose"), final_bg