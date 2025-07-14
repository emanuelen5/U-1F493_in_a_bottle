from machine import Pin
import time

DATA_PIN = Pin(2, Pin.IN, Pin.PULL_UP)
CLOCK_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

scan_bits = 0
scan_idx = 0

BUFFER_SIZE = 4  # Stores up to 3 bytes
scan_buffer = [0] * BUFFER_SIZE
buffer_head = 0  # Next write pos
buffer_tail = 0  # Next read pos

def ps2_irq_handler(pin):
    global scan_bits, scan_idx, scan_buffer, buffer_head, buffer_tail

    scan_bits |= (DATA_PIN.value() << scan_idx)
    scan_idx += 1

    if scan_idx == 11:
        if (scan_bits & 0x1) == 0 and ((scan_bits >> 10) & 0x1) == 1:
            code = (scan_bits >> 1) & 0xFF
            next_head = (buffer_head + 1) % BUFFER_SIZE
            if next_head != buffer_tail:  # Buffer not full
                scan_buffer[buffer_head] = code
                buffer_head = next_head
            # else: buffer full, discard new code
        scan_bits = 0x7FF
        scan_idx = 0

CLOCK_PIN.irq(trigger=Pin.IRQ_FALLING, handler=ps2_irq_handler)

def read_scan_code():
    global scan_buffer, buffer_head, buffer_tail
    if buffer_head == buffer_tail:
        return None  # Buffer empty
    code = scan_buffer[buffer_tail]
    buffer_tail = (buffer_tail + 1) % BUFFER_SIZE
    return code

# Example main loop
while True:
    code = read_scan_code()
    if code is not None:
        print("Scan code: {:02X}".format(code))
        time.sleep(0.5)
    else:
        time.sleep(0.01)
