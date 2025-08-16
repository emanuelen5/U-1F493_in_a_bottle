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

while True:
    gc.collect()

    while scan_code := ps2.get_scan_code():
        kbd.process_code(scan_code)

    if ps2.get_parity_error_count() > 0:
        lcd.clear()
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

    charcodes = []
    for c in reversed(full_text):
        if len(charcodes) >= 31:
            break

        charcode = keycode_map.get(c, None)
        if charcode is None:
            continue

        charcodes.insert(0, charcode)

    text_len = len(charcodes)
    lcd.move_to(0, 0)
    for i, c in enumerate(charcodes, start=1):
        lcd.hal_write_data(c)
        if i == 16:
            lcd.move_to(0, 1)
    for _ in range(max(0, 32 - text_len)):
        lcd.hal_write_data(ord(" "))
    if text_len > 32:
        lcd.move_to(15, 1)
    else:
        lcd.move_to(text_len % 16, text_len // 16)
