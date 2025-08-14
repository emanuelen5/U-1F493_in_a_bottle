from keyboard import KeyboardTracker, Key
from lcd import setup_lcd
from logbook import Logbook
from ps2_pio import PS2PIODriver
from hd44780 import get_japanese_keycode_map, add_missing_characters

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3)
kbd = KeyboardTracker(verbose=True)

lcd = setup_lcd()

keycode_map = get_japanese_keycode_map()
add_missing_characters(lcd, keycode_map)

print("Main loop started with PIO driver")

full_text = ""
log = Logbook("logbook.txt")

while True:
    while scan_code := ps2.get_scan_code():
        kbd.process_code(scan_code)

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
        elif key.char in keycode_map:
            full_text += key.char

    charcodes = []
    for c in reversed(full_text):
        if len(charcodes) >= 32:
            break

        charcode = keycode_map.get(c, None)
        if charcode is None:
            continue

        charcodes.insert(0, charcode)

    lcd.clear()
    for c in charcodes:
        lcd.putchar(chr(c))
