from content import Chara_animation
from character_setting import Character_type, character_setting
from jump_in_character import jump_in_character
from show_character import show_character

def enter_character(
    bg_copy,
    character_type: Character_type,
    chara_animation: Chara_animation,
):
    arg = {
        "bg_copy": bg_copy,
        "character_path": character_setting[character_type]["character_path"],
        "character_left": character_setting[character_type]["character_left"],
        "character_bottom": character_setting[character_type]["character_bottom"],
    }

    if chara_animation == "jump":
        return jump_in_character(**arg)

    return show_character(**arg)
