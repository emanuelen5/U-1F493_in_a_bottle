from lcd import test_main
from ps2_kb import scan_codes

while True:
    print("Starting LCD test...")
    test_main()

    if scan_codes:
        code = scan_codes.pop()
        print("Scan code: {:02X}".format(code))
