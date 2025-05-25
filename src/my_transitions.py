from moviepy.editor import CompositeVideoClip, ColorClip

def make_page_flip(clip1, clip2, duration=0.1):
    w, h = clip1.size

    # スライドイン位置
    def clip2_position(t):
        progress = min(1, t / duration)
        x = int(w * (1 - progress))
        return (x, 0)

    # 背景を白で固定
    white_bg = ColorClip(size=(w, h), color=(255, 255, 255)).set_duration(duration)

    # clip2 をスライドさせる
    moving_clip2 = clip2.set_position(clip2_position).set_start(0).set_duration(duration)

    # clip1 は静止状態のまま最後のフレームで固定
    clip1_final_frame = clip1.to_ImageClip(clip1.duration).set_duration(duration)

    # 合成：白背景 → clip1 → clip2
    transition = CompositeVideoClip(
        [white_bg, clip1_final_frame, moving_clip2], size=(w, h)
    ).set_duration(duration)

    return transition