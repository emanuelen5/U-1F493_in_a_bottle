"""
PS/2 Keyboard PIO Driver for Raspberry Pi Pico
Uses PIO state machine to receive PS/2 data frames
"""

import array

import rp2
from machine import Pin


class PS2PIODriver:
    def __init__(self, data_pin=2, clock_pin=3, led_pin=4, buffer_size=32):
        self.data_pin = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self.clock_pin = Pin(clock_pin, Pin.IN, Pin.PULL_UP)
        self.led_pin = Pin(led_pin, Pin.OUT)
        self.led_pin.value(1)

        # Circular buffer for scan codes
        self.buffer_size = buffer_size
        self.scan_buffer = array.array('H', [0] * buffer_size)
        self.buffer_head = 0
        self.buffer_tail = 0

        # Create and start the PIO state machine
        self.sm = rp2.StateMachine(
            0,
            self.ps2_pio_program,
            freq=1_000_000,  # 1MHz - much faster than PS/2 clock
            in_base=self.data_pin,
            jmp_pin=self.clock_pin,
            set_base=self.led_pin
        )
        self.sm.active(1)

    @rp2.asm_pio(
        in_shiftdir=rp2.PIO.SHIFT_RIGHT,
        autopush=True,
        push_thresh=11,  # Push after 11 bits (complete PS/2 frame)
        set_init=rp2.PIO.OUT_HIGH  # LED initially on
    )
    def ps2_pio_program():
        label("start_bit")
        wait(0, pin, 1)
        set(pins, 0)
        in_(pins, 1)

        set(x, 9) # Run 9 + 1 more iterations
        label("bit_loop")
        wait(1, pin, 1)
        wait(0, pin, 1)
        in_(pins, 1)

        jmp(x_dec, "bit_loop")

        wait(1, pin, 1)
        set(pins, 1)
        # Loop back to start

    def read_scan_code(self):
        """Read and validate a scan code from the PIO FIFO"""
        if self.sm.rx_fifo():
            # Get 11-bit frame from PIO
            frame = self.sm.get() >> 32 - 11

            # Extract components (PIO shifts right, so bits are in correct positions)
            start_bit = frame & 0x1
            data_bits = (frame >> 1) & 0xFF
            parity_bit = (frame >> 9) & 0x1
            stop_bit = (frame >> 10) & 0x1

            # Validate frame format
            if start_bit != 0 or stop_bit != 1:
                print(f"Invalid frame format: start={start_bit}, stop={stop_bit}, {data_bits=:03X}")
                return None

            # Check parity (PS/2 uses odd parity)
            parity_count = 0
            temp = data_bits
            while temp:
                parity_count += temp & 1
                temp >>= 1

            if (parity_count + parity_bit) & 1:
                return data_bits
            else:
                print(f"Parity error: frame={frame:03X}, data={data_bits:02X}")
                return None

        return None

    def get_available_codes(self):
        """Get all available scan codes as a list"""
        codes = []
        while True:
            code = self.read_scan_code()
            if code is None:
                break
            codes.append(code)
        return codes

    def deinit(self):
        """Clean up the PIO state machine"""
        self.sm.active(0)
