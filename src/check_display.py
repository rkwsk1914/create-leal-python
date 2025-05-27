import sys
import json
from moviepy.editor import concatenate_videoclips
from generate_scene_top import generate_scene_top
from generate_scene import generate_scene
from my_transitions import make_page_flip
from setting import default_fps

def build_video(scenes, transition_duration=0.3, fps=default_fps, output_path="dist/output.mp4"):
    clips = []

    for i in range(len(scenes)):
        scene_clip = scenes[i]()  # 関数を呼び出す

        if i == 0:
            clips.append(scene_clip)
        else:
            prev_clip = clips[-1]
            prev_main = prev_clip.subclip(0, prev_clip.duration - transition_duration)
            prev_end_frame = prev_clip.to_ImageClip(prev_clip.duration - transition_duration).set_duration(transition_duration)

            next_start_frame = scene_clip.to_ImageClip(0).set_duration(transition_duration)
            transition = make_page_flip(prev_end_frame, next_start_frame, duration=transition_duration)
            next_main = scene_clip.set_start(0)

            clips[-1] = prev_main
            clips.extend([transition, next_main])

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=fps)

# ===== 引数チェック =====
# if len(sys.argv) < 3:
#     print("エラー: JSONファイルパスと出力ファイル名を指定してください")
#     print("使用例: python src/index.py data/content.json dist/output.mp4")
#     sys.exit(1)

json_path = sys.argv[1]
# output_path = sys.argv[2]

# ===== JSON を読み込む =====
try:
    with open(json_path, "r", encoding="utf-8") as f:
        contents = json.load(f)
except Exception as e:
    print(f"JSONの読み込みエラー: {e}")
    sys.exit(1)

# ===== 動画のシーンを生成 =====
scenes = []

for content_item in contents:
    leal_title = content_item["leal_title"]
    leal_number = content_item["leal_number"]

    scenes.append(lambda item=content_item: generate_scene_top(
        character_type=item["chara_type"],
        chara_animation=item["chara_animation"],
        title=item["leal_title"],
        leal_number=item["leal_number"],
        with_animation=False
    ))

    for block in content_item["content"]:
        def make_block_func(block=block):
            return lambda: generate_scene(
                character_type=block["chara_type"],
                chara_animation=block["chara_animation"],
                title=[block["title"]],
                contents=block["content"],
                leal_title=leal_title,
                leal_number=leal_number,
                with_animation=False
            )
        scenes.append(make_block_func())

# ===== 動画出力 =====
build_video(scenes, output_path="check/check.mp4")