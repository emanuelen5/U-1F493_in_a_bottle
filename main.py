from lcd import setup_lcd
from ps2_kb import read_scan_code

keys = []
lcd = setup_lcd()

print("Main loop started")

while True:
    scan_code = read_scan_code()
    if scan_code:
        print("Scan code: {:02X}".format(scan_code))
        keys.append(scan_code)

        lcd.clear()

        string = "".join([chr(a) for a in keys])
        lcd.putstr(string)
