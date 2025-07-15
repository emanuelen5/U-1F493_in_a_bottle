from machine import Pin

DATA_PIN = Pin(2, Pin.IN, Pin.PULL_UP)
CLOCK_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

scan_bits = 0x7FF  # Start with all bits set

BUFFER_SIZE = 4  # Stores up to 3 bytes
scan_buffer = [0] * BUFFER_SIZE
buffer_head = 0  # Next write pos
buffer_tail = 0  # Next read pos


def ps2_irq_handler(pin):
    global scan_bits, scan_buffer, buffer_head, buffer_tail

    # Shift right and add new bit at position 10 (MSB)
    scan_bits = (scan_bits >> 1) | (DATA_PIN.value() << 10)

    # Check if we have a valid frame (start bit 0, stop bit 1)
    start_bit = scan_bits & 0x1
    stop_bit = (scan_bits >> 10) & 0x1
    if start_bit == 0 and stop_bit == 1:
        # Store the raw 11-bit frame for later processing
        next_head = (buffer_head + 1) % BUFFER_SIZE
        if next_head != buffer_tail:  # Buffer not full
            scan_buffer[buffer_head] = scan_bits  # Store full frame
            buffer_head = next_head

        # Reset scan_bits after processing
        scan_bits = 0x7FF


CLOCK_PIN.irq(trigger=Pin.IRQ_FALLING, handler=ps2_irq_handler)


def read_scan_code():
    global scan_buffer, buffer_head, buffer_tail

    while buffer_head != buffer_tail:
        frame = scan_buffer[buffer_tail]
        buffer_tail = (buffer_tail + 1) % BUFFER_SIZE

        # Extract components from the frame
        code = (frame >> 1) & 0xFF
        parity_bit = (frame >> 9) & 0x1

        # Check parity: count 1s in data bits
        parity_count = 0
        temp = code
        while temp:
            parity_count += temp & 1
            temp >>= 1

        # PS/2 uses odd parity - return code if parity is correct
        if (parity_count + parity_bit) & 1:
            return code
        # If parity is wrong, skip this frame and try next
        print(f"Bad parity for frame: {frame:03X}, expected odd parity")

    return None  # Buffer empty or all frames had bad parity
