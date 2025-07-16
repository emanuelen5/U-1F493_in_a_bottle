from keyboard import SCAN_CODE_MAP
from lcd import setup_lcd
from ps2_pio import PS2PIODriver

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3, led_pin=4)

scan_codes = []
lcd = setup_lcd()

print("Main loop started with PIO driver")

full_text = ""

while True:
    # Get all available scan codes from PIO driver
    new_codes = ps2.get_available_codes()
    scan_codes.extend(new_codes)

    if scan_codes and scan_codes[0] in (0xF0, 0xE0):
        if len(scan_codes) >= 2:
            scan_codes = scan_codes[2:]

    elif scan_codes:
        keys = "".join([SCAN_CODE_MAP.get(code, "?") for code in scan_codes])
        print(f"Keys: {scan_codes=}, {keys=}")
        scan_codes.clear()

        valid_keys = keys.replace("?", "")
        lcd.putstr(valid_keys)
        full_text += valid_keys
