import array
import time
import math
from machine import Pin
import rp2


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def neopixel_pio():
    HIGH_CYCLES = 2
    LOW_CYCLES = 5
    RESET_CYCLES = 3

    wrap_target()
    label("bit_start")
    out(x, 1)                    .side(0)    [RESET_CYCLES - 1]
    jmp(not_x, "send_zero")      .side(1)    [HIGH_CYCLES - 1]
    jmp("bit_start")             .side(1)    [LOW_CYCLES - 1]
    label("send_zero")
    nop()                        .side(0)    [LOW_CYCLES - 1]
    wrap()


class WS2812B_Driver:
    def __init__(self, pin_num: int, led_count: int, state_machine_id: int = 0) -> None:
        self.pin: Pin = Pin(pin_num, Pin.OUT)
        self.led_count: int = led_count
        self.sm_id: int = state_machine_id
        self.brightness_factor: float = 1.0
        self.pixel_buffer: array.array = array.array("I", [0 for _ in range(led_count)])
        self._setup_pio()

    def _setup_pio(self) -> None:
        self.state_machine = rp2.StateMachine(
            self.sm_id,
            neopixel_pio,
            freq=8_000_000,
            sideset_base=self.pin
        )
        self.state_machine.active(1)

    def _convert_rgb_to_grb(self, red: int, green: int, blue: int) -> int:
        red = int(red * self.brightness_factor) & 0xFF
        green = int(green * self.brightness_factor) & 0xFF
        blue = int(blue * self.brightness_factor) & 0xFF
        return (green << 16) | (red << 8) | blue

    def set_led(self, index: int, red: int, green: int, blue: int) -> None:
        if 0 <= index < self.led_count:
            self.pixel_buffer[index] = self._convert_rgb_to_grb(red, green, blue)

    def fill_strip(self, red: int, green: int, blue: int) -> None:
        color_value = self._convert_rgb_to_grb(red, green, blue)
        for i in range(self.led_count):
            self.pixel_buffer[i] = color_value

    def update_strip(self) -> None:
        dimmer_arr = array.array("I", [0xFFFFFF00 >> 8])
        self.state_machine.put(dimmer_arr, 8)

        for pixel_data in self.pixel_buffer:
            self.state_machine.put(pixel_data, 8)

        time.sleep_us(100)

    def clear_all(self) -> None:
        self.fill_strip(0, 0, 0)
        self.update_strip()

    def set_brightness(self, level: float) -> None:
        self.brightness_factor = max(0.0, min(1.0, level))

    def get_led_count(self) -> int:
        return self.led_count

    def rainbow_cycle(self, speed: float = 0.01) -> None:
        for offset in range(1000):
            for i in range(self.led_count):
                hue = ((i * 256 // self.led_count) + offset) % 256
                red = int(127 * (1 + math.sin(hue * 2 * math.pi / 256)))
                green = int(127 * (1 + math.sin((hue + 85) * 2 * math.pi / 256)))
                blue = int(127 * (1 + math.sin((hue + 170) * 2 * math.pi / 256)))
                self.set_led(i, red, green, blue)
            self.update_strip()
            time.sleep(speed)


if __name__ == "__main__":
    led_strip = WS2812B_Driver(pin_num=15, led_count=10, state_machine_id=1)
    led_strip.set_brightness(1.0)

    led_strip.rainbow_cycle(speed=0.0)