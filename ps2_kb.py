import time

from machine import Pin

# Use GP2 for Data, GP3 for Clock
DATA_PIN = Pin(2, Pin.IN, Pin.PULL_UP)
CLOCK_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

scan_bits = []
scan_ready = False
scan_codes: list[int] = []


def ps2_irq_handler(pin):
    global scan_bits, scan_ready, scan_codes
    scan_bits.append(DATA_PIN.value())
    if len(scan_bits) == 11:
        # Process the complete scan code
        bits = scan_bits.copy()
        scan_bits = []
        scan_ready = False

        # Extract data bits (bits 1-8, excluding start, parity, and stop bits)
        data_bits = bits[1:9]
        value = 0
        for i, bit in enumerate(data_bits):
            value |= bit << i

        # Append the scan code to the list
        scan_codes.append(value)
        scan_ready = True


CLOCK_PIN.irq(trigger=Pin.IRQ_FALLING, handler=ps2_irq_handler)
