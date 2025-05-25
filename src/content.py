from typing import TypedDict, Literal, List, Union
from character_setting import Character_type

Chara_animation = Literal["jump", "none"]

class ContentBlock(TypedDict):
    title: str
    chara_type: Character_type
    chara_animation: Chara_animation
    content: List[Union[str, dict]]  # dictは画像などに使う

class ContentItem(TypedDict):
    lead_title: str
    content: List[ContentBlock]

contents: List[ContentItem] = [
    {
        "lead_title": ["ようこそ！", "自己紹介"],
        "chara_type": "surprised",
        "chara_animation": "jump",
        "content": [
            {
                "title": "次へ",
                "chara_type": "understand",
                "chara_animation": "none",
                "content": [
                    "準備はいいですか？",
                    "次に進みましょう。"
                ]
            },
            {
                "title": "次へ",
                "chara_type": "listen",
                "chara_animation": "none",
                "content": [
                    "準備はいいですか？",
                    "add_asset/maru.png"
                ]
            },
            {
                "title": "次へ",
                "chara_type": "understand",
                "chara_animation": "none",
                "content": [
                    "準備はいいですか？",
                    "次に進みましょう。"
                ]
            },
            {
                "title": "最後",
                "chara_type": "agree",
                "chara_animation": "jump",
                "content": [
                    "準備はいいですか？",
                    "次に進みましょう。"
                ]
            }
        ]
    }
]