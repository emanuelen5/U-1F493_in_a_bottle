"""
PS/2 Keyboard scan code to key mapping and tracking
Handles letters, numbers, and shift key state
"""

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

    # Special keys
    0x29: ' ',  # Space
    0x5A: '\n', # Enter
    0x66: '\b', # Backspace
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

# Shift key scan codes
SHIFT_LEFT = 0x12
SHIFT_RIGHT = 0x59

class KeyboardTracker:
    def __init__(self):
        self.keys = ""  # String to store all pressed keys
        self.shift_pressed = False
        self.last_scan_codes = []  # Keep track of recent scan codes for debugging

    def process_scan_code(self, scan_code):
        """Process a scan code and update the keys string"""
        # Keep track of recent scan codes for debugging
        self.last_scan_codes.append(scan_code)
        if len(self.last_scan_codes) > 10:
            self.last_scan_codes.pop(0)

        # Check for break codes (key release)
        if scan_code == 0xF0:
            # Next scan code will be a break code
            return

        # Handle shift keys
        if scan_code == SHIFT_LEFT or scan_code == SHIFT_RIGHT:
            self.shift_pressed = True
            return

        # Check if this is a release of shift key
        if len(self.last_scan_codes) >= 2 and self.last_scan_codes[-2] == 0xF0:
            if scan_code == SHIFT_LEFT or scan_code == SHIFT_RIGHT:
                self.shift_pressed = False
                return

        # Only process key presses (not releases)
        if len(self.last_scan_codes) >= 2 and self.last_scan_codes[-2] == 0xF0:
            # This is a key release, ignore it
            return

        # Map scan code to character
        char = SCAN_CODE_MAP.get(scan_code)
        if char is None:
            return

        # Apply shift if needed
        if self.shift_pressed:
            if char.isalpha():
                char = char.upper()
            elif char in SHIFTED_NUMBERS:
                char = SHIFTED_NUMBERS[char]

        # Handle special characters
        if char == '\b':  # Backspace
            if self.keys:
                self.keys = self.keys[:-1]
        elif char == '\n':  # Enter
            self.keys += char
        else:
            self.keys += char

    def get_keys_string(self):
        """Return the current keys string"""
        return self.keys

    def clear_keys(self):
        """Clear the keys string"""
        self.keys = ""

    def get_last_scan_codes(self):
        """Get recent scan codes for debugging"""
        return self.last_scan_codes.copy()

    def is_shift_pressed(self):
        """Check if shift is currently pressed"""
        return self.shift_pressed

# Global keyboard tracker instance
keyboard = KeyboardTracker()

def process_keyboard_input(scan_codes_list):
    """Process a list of scan codes and update the keyboard state"""
    for scan_code in scan_codes_list:
        keyboard.process_scan_code(scan_code)

def get_typed_text():
    """Get the current typed text"""
    return keyboard.get_keys_string()

def clear_typed_text():
    """Clear the typed text"""
    keyboard.clear_keys()

def is_shift_held():
    """Check if shift is currently held down"""
    return keyboard.is_shift_pressed()
