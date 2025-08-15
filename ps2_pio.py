"""
PS/2 Keyboard PIO Driver for Raspberry Pi Pico
Uses PIO state machine to receive PS/2 data frames
"""

import rp2
from machine import Pin


def has_ok_parity(frame: int):
    parity_count = 0
    temp = frame
    while temp:
        parity_count += temp & 1
        temp >>= 1

    return parity_count & 1 == 0


class PS2PIODriver:
    def __init__(self, data_pin: int, clock_pin: int):
        self.data_pin = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self.clock_pin = Pin(clock_pin, Pin.IN, Pin.PULL_UP)

        # Create and start the PIO state machine
        self.sm = rp2.StateMachine(
            0,
            self.ps2_pio_program,
            freq=1_000_000,  # 1MHz - much faster than PS/2 clock
            in_base=self.data_pin,
            jmp_pin=self.clock_pin,
        )
        self.sm.active(1)

    @rp2.asm_pio(
        in_shiftdir=rp2.PIO.SHIFT_RIGHT,
        autopush=True,
        push_thresh=11,  # Push after 11 bits (complete PS/2 frame)
        fifo_join=rp2.PIO.JOIN_RX,  # Join RX FIFO with TX, to make it twice as big
    )
    def ps2_pio_program():
        label("start_bit")
        wait(0, pin, 1)
        in_(pins, 1)

        set(x, 9)  # Run 9 + 1 more iterations
        label("bit_loop")
        wait(1, pin, 1)
        wait(0, pin, 1)
        in_(pins, 1)

        jmp(x_dec, "bit_loop")

        wait(1, pin, 1)
        # Loop back to start

    def get_scan_code(self):
        if not self.sm.rx_fifo():
            return None

        # The PIO FIFO returns a 32-bit frame
        frame: int = self.sm.get() >> (32 - 11)

        start_bit = frame & 0x1
        data_bits = (frame >> 1) & 0xFF
        stop_bit = (frame >> 10) & 0x1

        if start_bit != 0 or stop_bit != 1:
            print(
                f"Invalid frame format: start={start_bit}, stop={stop_bit}, {data_bits=:03X}"
            )
            return None

        if not has_ok_parity(frame):
            print(f"Parity error: frame={frame:03X}, data={data_bits:02X}")
            return None

        return data_bits

    def deinit(self):
        """Clean up the PIO state machine"""
        self.sm.active(0)
