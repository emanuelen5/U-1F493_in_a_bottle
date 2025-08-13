from keyboard import SCAN_CODE_MAP
from lcd import setup_lcd
from logbook import Logbook
from ps2_pio import PS2PIODriver
from hd44780 import get_japanese_keycode_map, add_missing_characters

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3)

scan_codes = []
lcd = setup_lcd()

keycode_map = get_japanese_keycode_map()
add_missing_characters(lcd, keycode_map)

print("Main loop started with PIO driver")

full_text = ""
log = Logbook("logbook.txt")

while True:
    while scan_code := ps2.get_scan_code():
        scan_codes.append(scan_code)

    if scan_codes and scan_codes[0] in (0xF0, 0xE0):
        if len(scan_codes) >= 2:
            scan_codes = scan_codes[2:]

    elif scan_codes:
        chars = "".join([SCAN_CODE_MAP.get(code, "") for code in scan_codes])
        keycodes = [keycode_map.get(char, None) for char in chars]
        print(f"Keys: {scan_codes=}, {chars=} {keycodes=}")
        scan_codes.clear()

        for keycode in keycodes:
            if keycode is None:
                continue

            lcd.putchar(chr(keycode))

        for c in chars:
            if "\n" == c:
                log.write_entry(full_text)
                lcd.clear()
                full_text = ""
            elif c == "\b":
                full_text = full_text[:-1]
                lcd.move_to(lcd.cursor_x - 1, lcd.cursor_y)
                lcd.putchar(" ")
                lcd.move_to(lcd.cursor_x - 1, lcd.cursor_y)
            else:
                full_text += c
