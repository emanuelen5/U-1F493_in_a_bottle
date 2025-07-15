from keyboard import SCAN_CODE_MAP
from lcd import setup_lcd
from ps2_kb import read_scan_code, scan_bits

scan_codes = []
lcd = setup_lcd()

last_scan_bits = scan_bits
print(f"Main loop started, {last_scan_bits=}, {scan_bits=}")

valid_keys = ""

while True:
    while scan_code := read_scan_code():
        scan_codes.append(scan_code)

    if scan_codes:
        keys = "".join([SCAN_CODE_MAP.get(code, "?") for code in scan_codes])
        print(f"Keys: {scan_codes=}, {keys=}")
        scan_codes.clear()

        valid_keys = valid_keys + keys.replace("?", "")

        lcd.clear()
        lcd.putstr(valid_keys)

    if scan_bits != last_scan_bits:
        print(f"Current scan bits {last_scan_bits=}, {scan_bits=}")
    last_scan_bits = scan_bits
