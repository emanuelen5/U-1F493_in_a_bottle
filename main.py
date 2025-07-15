from lcd import setup_lcd
from ps2_kb import read_scan_code, scan_bits

keys = []
lcd = setup_lcd()

last_scan_bits = scan_bits
print(f"Main loop started, {last_scan_bits=}, {scan_bits=}")

while True:
    scan_code = read_scan_code()
    if scan_code:
        print("Scan code: {:02X}".format(scan_code))
        keys.append(scan_code)

        lcd.clear()

        string = "".join([chr(a) for a in keys])
        lcd.putstr(string)
    
    if scan_bits != last_scan_bits:
        print(f"Current scan bits {last_scan_bits=}, {scan_bits=}")
    last_scan_bits = scan_bits
