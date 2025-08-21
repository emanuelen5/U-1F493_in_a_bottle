import math
import utime
from ws2812b_pio import WS2812B_Driver


class Pulse:
    def __init__(self, red, green, blue, width, lifetime_ms):
        self.activate(red, green, blue, width, lifetime_ms, active=False)

    def activate(self, red, green, blue, width, lifetime_ms, active=True):
        self.red = red
        self.green = green
        self.blue = blue
        self.width = width
        self.lifetime_ms = lifetime_ms
        self.start_time = utime.ticks_ms()
        self.active = active

    def get_progress(self):
        now = utime.ticks_ms()
        elapsed = utime.ticks_diff(now, self.start_time)
        progress = min(1.0, max(0.0, elapsed / self.lifetime_ms))
        return progress

    def get_position(self):
        # Returns normalized position (0-1)
        # Use cosine-based movement for smooth start/end
        progress = self.get_progress()
        angle = math.pi * progress  # 0 to π
        pos = (-math.cos(angle) + 1) / 2  # 0 to 1
        return pos

    def advance(self):
        if self.get_progress() >= 1.0:
            self.active = False


class LingeringPulse(Pulse):
    def __init__(self, offset, red, green, blue, width, lifetime_ms):
        self.offset = offset
        super().activate(red, green, blue, width, lifetime_ms, active=True)

    def advance(self):
        return

    def get_progress(self):
        now = utime.ticks_ms()
        elapsed = utime.ticks_diff(now, self.start_time)
        elapsed = elapsed / self.lifetime_ms

        progress = (math.sin(elapsed) * math.sin(1.235 * elapsed + self.offset) - ((math.sin(0.09 * elapsed + self.offset) + 1) * 13))
        return progress

    def get_position(self):
        return self.offset + self.get_progress() / 50


class LedAnimator:
    def __init__(self, led_strip: WS2812B_Driver):
        self.led_strip = led_strip
        self.pulses = [Pulse(0, 0, 0, 0, 0) for _ in range(10)]
        self.last_service = utime.ticks_ms()

    def add_pulse(self, pulse: Pulse):
        self.pulses.append(pulse)

    def add_wandering_pulse(self, red: int, green: int, blue: int, width: float = 3.0, lifetime_ms: int = 2000):
        pulse: None | Pulse = None
        for i in range(len(self.pulses)):
            if not self.pulses[i].active:
                pulse = self.pulses[i]
                break
        else:
            print("All pulses are allocated, cannot add more.")
            return

        pulse.activate(red, green, blue, width, lifetime_ms)

    def service(self):
        led_count = self.led_strip.led_count
        led_values = [(0, 0, 0) for _ in range(led_count)]

        for pulse in self.pulses:
            if not pulse.active:
                continue

            # Calculate normalized position (0-1)
            pos = pulse.get_position()
            # Map to LED index range, but allow pulse to start before 0 and end after last LED
            start_pos = -pulse.width * 3
            end_pos = led_count + pulse.width * 3
            center = start_pos + pos * (end_pos - start_pos)

            # Determine the range of LEDs affected by this pulse
            min_led = max(0, int(center - pulse.width * 3))
            max_led = min(led_count - 1, int(center + pulse.width * 3))

            for i in range(min_led, max_led + 1):  # Only iterate over affected LEDs
                dist = abs(i - center)
                fade = math.exp(-0.5 * (dist / pulse.width) ** 2)
                edge_fade = 0.7 + 0.3 * fade
                r = int(pulse.red * fade * edge_fade)
                g = int(pulse.green * fade * edge_fade)
                b = int(pulse.blue * fade * edge_fade)
                cr, cg, cb = led_values[i]
                led_values[i] = (
                    min(255, cr + r),
                    min(255, cg + g),
                    min(255, cb + b)
                )
            pulse.advance()

        for i, (r, g, b) in enumerate(led_values):
            self.led_strip.set_led(i, r, g, b)
        self.led_strip.update_strip()


# Standalone demo
if __name__ == "__main__":
    import utime

    from ws2812b_pio import WS2812B_Driver
    LED_COUNT = 50
    led_strip = WS2812B_Driver(pin_num=15, led_count=LED_COUNT, state_machine_id=1)
    animator = LedAnimator(led_strip)

    pulse_interval_ms = 2000  # Add a new pulse every second
    last_pulse_time = utime.ticks_ms()

    print("Starting LED animator demo...")
    animator.add_pulse(LingeringPulse(offset=0.9, red=20, green=0, blue=5, width=1, lifetime_ms=500))
    while True:
        now = utime.ticks_ms()
        if utime.ticks_diff(now, last_pulse_time) > pulse_interval_ms:
            animator.add_wandering_pulse(
                red=64, green=0, blue=128, width=2.0, lifetime_ms=5000
            )
            last_pulse_time = now
        animator.service()
        utime.sleep_ms(20)
