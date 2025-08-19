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

# Special key constants for cursor movement and editing
key_left_arrow = '\x1b[D'   # ASCII escape sequence for left arrow
key_right_arrow = '\x1b[C'  # ASCII escape sequence for right arrow
key_up_arrow = '\x1b[A'     # ASCII escape sequence for up arrow
key_down_arrow = '\x1b[B'   # ASCII escape sequence for down arrow
key_home = '\x1b[H'         # Home key (move to start)
key_end = '\x1b[F'          # End key (move to end)
key_page_up = '\x1b[5~'     # Page Up
key_page_down = '\x1b[6~'   # Page Down

# PS/2 scan code to key mapping for letters and numbers
key_map = {
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

    # Arrow keys (using E0 extended codes)
    0xE075: key_up_arrow,
    0xE072: key_down_arrow,
    0xE06B: key_left_arrow,
    0xE074: key_right_arrow,

    # Navigation keys
    0xE06C: key_home,
    0xE069: key_end,
    0xE07D: key_page_up,
    0xE07A: key_page_down,

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

shift_key_map = {
    # Numbers (top row)
    0x45: '=',
    0x16: '!',
    0x1E: '"',
    0x26: '#',
    0x25: '¤',
    0x2E: '%',
    0x36: '&',
    0x3D: '/',
    0x3E: '(',
    0x46: ')',
    0x4e: '?',
    0x55: '`',

    # Punctuation
    0x41: ';',
    0x49: ':',
    0x4a: '_',
    0x61: '>',
    0x0e: '~',
    0x5d: "*",
    0x5b: "^",

    # Letters (QWERTY layout)
    0x1C: 'A',
    0x32: 'B',
    0x21: 'C',
    0x23: 'D',
    0x24: 'E',
    0x2B: 'F',
    0x34: 'G',
    0x33: 'H',
    0x43: 'I',
    0x3B: 'J',
    0x42: 'K',
    0x4B: 'L',
    0x3A: 'M',
    0x31: 'N',
    0x44: 'O',
    0x4D: 'P',
    0x15: 'Q',
    0x2D: 'R',
    0x1B: 'S',
    0x2C: 'T',
    0x3C: 'U',
    0x2A: 'V',
    0x1D: 'W',
    0x22: 'X',
    0x35: 'Y',
    0x1A: 'Z',

    # no font for uppercase umlauts
    84: 'å',
    82: 'ä',
    76: 'ö',

    # Special keys
    0x29: ' ',  # Space
    0x5A: '\n', # Enter
    0x66: '\b\b', # Backspace
}

ctrl_alt_key_map = {
    0x1E: "@",
    0x26: "£",
    0x25: "$",
}

ctrl_key_map = {
    0x66: '\b\b', # Backspace
}

modifiers = str
pressed = True
released = False


class Key:
    def __init__(self, char: str):
        self.char = char


release_code_prefix = 0xF0
extended_code_prefix = 0xE0


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
        self._extended_keycode = False
        self._released_key = False

        self.key_presses: list[str] = []

    def _process_code(self, code: int):
        if self._extended_keycode:
            code = (extended_code_prefix << 8) | code

        modifier_name = self.modifier_codes.get(code, None)
        if modifier_name:
            got_pressed = not self._released_key
            if self.verbose:
                print(f"modifier: {modifier_name}={got_pressed}")
            self.keys_state[modifier_name] = got_pressed
            return

        if self._released_key:
            return

        shift_down = self.is_key_pressed("LeftShift") or self.is_key_pressed("RightShift")
        ctrl_down = self.is_key_pressed("LeftCtrl") or self.is_key_pressed("RightCtrl")
        alt_down = self.is_key_pressed("LeftAlt") or self.is_key_pressed("RightAlt")

        char = None
        if shift_down and not ctrl_down and not alt_down:
            char = shift_key_map.get(code, None)
        elif not shift_down and ctrl_down and not alt_down:
            char = ctrl_key_map.get(code, None)
        elif not shift_down and ctrl_down and alt_down:
            char = ctrl_alt_key_map.get(code, None)
        elif not shift_down and not ctrl_down and not alt_down:
            char = key_map.get(code, None)

        if self.verbose:
            print(f"Scan code: {code} (0x{code:02x}), {char=}")

        if char is None:
            return None

        self.key_presses.append(char)

    def process_code(self, code: int):
        if code == extended_code_prefix:
            self._extended_keycode = True
            return
        elif code == release_code_prefix:
            self._released_key = True
            return
        else:
            self._process_code(code)
            self._extended_keycode = False
            self._released_key = False

    def get_keypress(self) -> Key | None:
        if not self.key_presses:
            return None

        return Key(self.key_presses.pop(0))

    def is_key_pressed(self, key: modifiers) -> bool:
        return self.keys_state[key]
