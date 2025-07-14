import I2C
import machine
import utime

from i2c_lcd import I2cLcd

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16


def test_main():
    # Test function for verifying basic functionality
    i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    lcd.putstr("It Works!")
    utime.sleep(2)
    lcd.clear()
    for count in range(8):
        lcd.clear()
        time = utime.localtime()
        lcd.putstr(
            "{year:>04d}/{month:>02d}/{day:>02d} {HH:>02d}:{MM:>02d}:{SS:>02d}".format(
                year=time[0],
                month=time[1],
                day=time[2],
                HH=time[3],
                MM=time[4],
                SS=time[5],
            )
        )
        if count % 10 == 0:
            print("Turning cursor on")
            lcd.show_cursor()
        elif count % 10 == 1:
            print("Turning cursor off")
            lcd.hide_cursor()
        elif count % 10 == 2:
            print("Turning blink cursor on")
            lcd.blink_cursor_on()
        elif count % 10 == 3:
            print("Turning blink cursor off")
            lcd.blink_cursor_off()
        elif count % 10 == 4:
            print("Turning backlight off")
            lcd.backlight_off()
        elif count % 10 == 5:
            print("Turning backlight on")
            lcd.backlight_on()
        elif count % 10 == 6:
            print("Turning display off")
            lcd.display_off()
        elif count % 10 == 7:
            print("Turning display on")
            lcd.display_on()
        elif count % 10 == 8:
            print("Filling display")
            lcd.clear()
            string = ""
            for x in range(32, 32 + I2C_NUM_ROWS * I2C_NUM_COLS):
                string += chr(x)
            lcd.putstr(string)

        utime.sleep(2)
