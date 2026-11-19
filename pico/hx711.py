"""HX711 yük hücresi yükselticisi için küçük MicroPython sürücüsü (A kanalı, kazanç 128)."""
import time

from machine import Pin


class HX711:
    def __init__(self, dt_pin, sck_pin):
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sck = Pin(sck_pin, Pin.OUT, value=0)

    def hazir(self):
        return self.dt.value() == 0

    def oku(self, zaman_asimi_ms=200):
        """24 bitlik işaretli ham değer; HX711 hazır olmazsa None."""
        bas = time.ticks_ms()
        while not self.hazir():
            if time.ticks_diff(time.ticks_ms(), bas) > zaman_asimi_ms:
                return None
            time.sleep_ms(1)
        deger = 0
        for _ in range(24):
            self.sck.value(1)
            self.sck.value(0)
            deger = (deger << 1) | self.dt.value()
        self.sck.value(1)               # 25. darbe: bir sonraki okuma A kanalı, kazanç 128
        self.sck.value(0)
        if deger & 0x800000:
            deger -= 0x1000000
        return deger

    def uyut(self):
        self.sck.value(1)
        time.sleep_us(80)
