from lcd import setup_lcd
from ps2_kb import scan_codes

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
