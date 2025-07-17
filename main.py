import time

from keyboard import SCAN_CODE_MAP
from lcd import setup_lcd
from ps2_pio import PS2PIODriver

# Initialize PS/2 PIO driver
ps2 = PS2PIODriver(data_pin=2, clock_pin=3)

scan_codes = []
lcd = setup_lcd()

print("Main loop started with PIO driver")

full_text = ""

while True:
    while scan_code := ps2.get_scan_code():
        scan_codes.append(scan_code)

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

        if "\n" in full_text:
            time = time.localtime()
            dt = "{:>04d}-{:>02d}-{:>02d} {:>02d}:{:>02d}:{:>02d}".format(*time)
            with open("output.txt", "a") as f:
                f.write(f"--- {dt}\n" + full_text + "\n")

            lcd.clear()
            full_text = ""
