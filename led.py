from machine import Pin
import time
import config

_led = Pin(config.LED_PIN, Pin.OUT)
_led.value(1)  # Aktif-düşük: 1 = kapalı


def blink(times=1, on_ms=150, off_ms=150):
    for _ in range(times):
        _led.value(0)
        time.sleep_ms(on_ms)
        _led.value(1)
        time.sleep_ms(off_ms)
