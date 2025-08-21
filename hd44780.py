from lcd_api import LcdApi

def get_japanese_keycode_map() -> dict[str, int]:
    # Japanese characters, ROM code: A00
    japanese_keycode_map: dict[str, int] = {
        " ": 0x20,
        "\n": 0x20,
        "\\": 0x56,
        "ä": 0xe1,
        "ö": 0xef,
    }

    # ASCII characters from ! to } are one to one, except for \
    for i in range(ord('!'), ord('}') + 1):
        if i == ord('\\'):
            continue

        japanese_keycode_map[chr(i)] = i
    
    return japanese_keycode_map


char_envelope_left = "⊂"
char_envelope_right = "⊃"


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
        0x0,0xa,0x1f,0x1f,0xe,0x4,0x0,0x0
    ])
    create_char(char_envelope_left, 2, [
        0b11111, 
        0b11000, 
        0b10100, 
        0b10010, 
        0b10001, 
        0b11111, 
        0b00000, 
        0b00000,
    ])
    create_char(char_envelope_right, 3, [
        0b11111, 
        0b00011, 
        0b00101, 
        0b01001, 
        0b10001, 
        0b11111, 
        0b00000, 
        0b00000,
    ])
