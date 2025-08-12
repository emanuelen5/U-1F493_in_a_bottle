from lcd_api import LcdApi

def get_japanese_keycode_map() -> dict[str, int]:
    # Japanese characters, ROM code: A00
    japanese_keycode_map: dict[str, int] = {
        " ": 0x29,
        "\n": 0x5A,
        "\\": 0xA4,
        "ä": 0xe1,
        "ö": 0xef,
    }

    # ASCII characters from ! to } are one to one, except for \
    for i in range(ord('!'), ord('}') + 1):
        if i == ord('\\'):
            continue

        japanese_keycode_map[chr(i)] = i
    
    return japanese_keycode_map


def add_missing_characters(lcd: LcdApi, keycode_map: dict[str, int]):
    """Set up special characters for the LCD."""
    def create_char(char: str, index: int, charmap: list[int]):
        cg_ram_address = index & 0x7
        keycode_map.update({
            char: cg_ram_address,
        })
        lcd.custom_char(index, charmap)

    # https://www.quinapalus.com/hd44780udg.html
    create_char("å", 0, [
        0x4,0x0,0xe,0x1,0xf,0x11,0xf,0x0
    ])
    create_char("♥", 1, [
        0x0,0xa,0x15,0x11,0xa,0x4,0x0,0x0
    ])
