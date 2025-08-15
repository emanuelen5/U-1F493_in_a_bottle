"""
PS/2 Keyboard scan code to key mapping and tracking
Handles letters, numbers, and shift key state
"""

key_f1 = "♥"
key_f2 = "☻"
key_f3 = "♦"
key_f4 = "♣"
key_f5 = "♠"
key_f6 = "•"
key_f7 = "◘"
key_f8 = "○"
key_f9 = "◙"
key_f10 = "♂"
key_f11 = "♀"
key_f12 = "♪"

# PS/2 scan code to key mapping for letters and numbers
SCAN_CODE_MAP = {
    # Numbers (top row)
    0x45: '0',
    0x16: '1',
    0x1E: '2',
    0x26: '3',
    0x25: '4',
    0x2E: '5',
    0x36: '6',
    0x3D: '7',
    0x3E: '8',
    0x46: '9',
    0x4e: '+',
    0x55: '´',

    # Punctuation
    0x41: ',',
    0x49: '.',
    0x4a: '-',
    0x61: '<',
    0x0e: '§',
    0x5d: "'",
    0x5b: "¨",

    # Letters (QWERTY layout)
    0x1C: 'a',
    0x32: 'b',
    0x21: 'c',
    0x23: 'd',
    0x24: 'e',
    0x2B: 'f',
    0x34: 'g',
    0x33: 'h',
    0x43: 'i',
    0x3B: 'j',
    0x42: 'k',
    0x4B: 'l',
    0x3A: 'm',
    0x31: 'n',
    0x44: 'o',
    0x4D: 'p',
    0x15: 'q',
    0x2D: 'r',
    0x1B: 's',
    0x2C: 't',
    0x3C: 'u',
    0x2A: 'v',
    0x1D: 'w',
    0x22: 'x',
    0x35: 'y',
    0x1A: 'z',

    84: 'å',
    82: 'ä',
    76: 'ö',

    # Special keys
    0x29: ' ',  # Space
    0x5A: '\n', # Enter
    0x66: '\b', # Backspace

    5: key_f1,
    6: key_f2,
    4: key_f3,
    12: key_f4,
    3: key_f5,
    11: key_f6,
    131: key_f7,
    10: key_f8,
    1: key_f9,
    9: key_f10,
    120: key_f11,
    7: key_f12,
}

# Shifted versions of numbers
SHIFTED_NUMBERS = {
    '0': ')',
    '1': '!',
    '2': '@',
    '3': '#',
    '4': '$',
    '5': '%',
    '6': '^',
    '7': '&',
    '8': '*',
    '9': '(',
}

modifiers = str
pressed = True
released = False


class Key:
    def __init__(self, char: str):
        self.char = char


class KeyboardTracker:
    def __init__(self, verbose: bool = False):
        self.keys_state: dict[modifiers, bool] = {
            "LeftShift": released,
            "LeftCtrl": released,
            "LeftAlt": released,
            "RightShift": released,
            "RightCtrl": released,
            "RightAlt": released,
        }
        self.modifier_codes: dict[int, modifiers] = {
            0x12: "LeftShift",
            0x14: "LeftCtrl",
            0x11: "LeftAlt",
            0x59: "RightShift",
            0xE014: "RightCtrl",
            0xE011: "RightAlt",
        }
        self.verbose = verbose

        self._previous_code = 0
        self.key_presses: list[str] = []

    def _process_code(self, code: int):
        release_code_prefix = 0xF0
        extended_code_prefix = 0xE0

        if code in (extended_code_prefix, release_code_prefix):
            return

        if self._previous_code == extended_code_prefix:
            code = (extended_code_prefix << 8) | code

        modifier_name = self.modifier_codes.get(code, None)
        if modifier_name:
            got_pressed = self._previous_code != release_code_prefix
            if self.verbose:
                print(f"modifier: {modifier_name}={got_pressed}")
            self.keys_state[modifier_name] = released if got_pressed else pressed
            return

        if self._previous_code == release_code_prefix:
            return

        char = SCAN_CODE_MAP.get(code, None)

        if self.verbose:
            print(f"Scan code: {code} (0x{code:02x}), {char=}")

        if char is None:
            return None

        self.key_presses.append(char)


    def process_code(self, code: int):
        self._process_code(code)
        self._previous_code = code

    def get_keypress(self) -> Key | None:
        if not self.key_presses:
            return None

        return Key(self.key_presses.pop(0))

    def is_key_pressed(self, key: modifiers) -> bool:
        return self.keys_state[key]
