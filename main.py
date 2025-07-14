from lcd import setup_lcd
from ps2_kb import check_bus_timeout, scan_codes

keys = []
lcd = setup_lcd()

while True:
    if scan_codes:
        code = scan_codes.pop()
        print("Scan code: {:02X}".format(code))
        keys.append(code)

        lcd.clear()

        string = "".join([chr(a) for a in keys])
        lcd.putstr(string)

    # Check for PS/2 bus timeout and clear scan_bits if needed
    check_bus_timeout()
