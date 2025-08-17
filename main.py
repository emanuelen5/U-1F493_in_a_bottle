from keyboard import KeyboardTracker, Key
from lcd import setup_lcd
from logbook import Logbook
from ps2_pio import PS2PIODriver
from hd44780 import get_japanese_keycode_map, add_missing_characters
import gc

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3)
kbd = KeyboardTracker(verbose=True)

lcd = setup_lcd()
lcd.blink_cursor_on()

keycode_map = get_japanese_keycode_map()
add_missing_characters(lcd, keycode_map)

print("Main loop started with PIO driver")

full_text = ""
log = Logbook("logbook.txt")

# Display buffer to track what's currently shown (2 lines × 16 chars)
display_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]

def update_display_optimized(text, keycode_map: dict[str, int]):
    """Update only the parts of the display that have changed"""
    global display_buffer

    # Convert text to character codes (last 31 chars, reversed order)
    charcodes = []
    for c in reversed(text):
        if len(charcodes) >= 31:
            break
        charcode = keycode_map.get(c, None)
        if charcode is None:
            continue
        charcodes.insert(0, charcode)

    # Create new display state
    new_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]

    # Fill the new buffer with the text
    for i, charcode in enumerate(charcodes):
        row = i // 16
        col = i % 16
        if row < 2:
            new_buffer[row][col] = charcode

    # Update only changed positions
    cursor_row, cursor_col = -1, -1  # Track where we think the cursor is
    for row in range(2):
        for col in range(16):
            if new_buffer[row][col] != display_buffer[row][col]:
                # Only move cursor if we're not already at the right position
                if cursor_row != row or cursor_col != col:
                    lcd.move_to(col, row)
                    cursor_row, cursor_col = row, col

                lcd.hal_write_data(new_buffer[row][col])
                display_buffer[row][col] = new_buffer[row][col]
                # Cursor automatically moves right after writing (but doesn't wrap)
                cursor_col += 1

    # Position cursor at the end of text
    text_len = len(charcodes)
    if text_len > 32:
        lcd.move_to(15, 1)
    else:
        lcd.move_to(text_len % 16, text_len // 16)

while True:
    gc.collect()

    while scan_code := ps2.get_scan_code():
        kbd.process_code(scan_code)

    if ps2.get_parity_error_count() > 0:
        lcd.clear()
        # Reset display buffer since we cleared the screen
        display_buffer = [[ord(" ") for _ in range(16)] for _ in range(2)]
        lcd.putstr("Parity error. Resetting PIO...")
        ps2.reset_sm()
        continue

    keys: list[Key] = []
    while key := kbd.get_keypress():
        keys.append(key)

    if not keys:
        continue

    for key in keys:
        if key.char == "\n":
            log.write_entry(full_text)
            full_text = ""
        elif key.char == "\b":
            full_text = full_text[:-1]
        elif key.char == "\b\b":
            idx = full_text.rfind(" ")
            if idx == -1:
                idx = 0
            full_text = full_text[:idx]
        elif key.char in keycode_map:
            full_text += key.char

    # Update display only with changed parts
    update_display_optimized(full_text, keycode_map)
