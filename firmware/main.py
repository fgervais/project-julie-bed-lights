import network
import time
import micropython
import esp32
import machine
import blynklib_mp as blynklib
import blynklib_mp_ssl as blynklib_ssl
import secret

from machine import Pin, PWM, ADC, TouchPad, RTC, UART


RED_PIN = 19
GREEN_PIN = 23
BLUE_PIN = 5

COLOR_VPIN = 0
BRIGHTNESS_VPIN = 1
ON_OFF_VPIN = 2


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("connecting to network...")
    wlan.connect(secret.ESSID, secret.PSK)
    while not wlan.isconnected():
        time.sleep(1)
print("network config:", wlan.ifconfig())


class LedStrip:
    def __init__(self, rgb_pins):
        self.pwms = [PWM(Pin(i), freq=4000, duty=0) for i in rgb_pins]
        self._on = False
        self._color = (0, 0, 0)
        self._brightnes = 0

    def on(self):
        self._on = True
        self.show()

    def off(self):
        self._on = False
        self.show()

    def show(self):
        if self._on:
            brightnes = self._brightnes
        else:
            brightnes = 0

        for index, value in enumerate(self._color):
            self.pwms[index].duty(int(value * brightnes))

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.show()

    @property
    def brightnes(self):
        return self._brightnes

    @brightnes.setter
    def brightnes(self, value):
        self._brightnes = value
        self.show()


strip = LedStrip([RED_PIN, GREEN_PIN, BLUE_PIN])

ssl_connection = blynklib_ssl.SslConnection(secret.BLYNK_AUTH, port=443, log=print)
blynk = blynklib.Blynk(secret.BLYNK_AUTH, connection=ssl_connection)


@blynk.handle_event("write V" + str(COLOR_VPIN))
def write_handler(pin, value):
    strip.color = tuple(map(int, value))

@blynk.handle_event("write V" + str(BRIGHTNESS_VPIN))
def write_handler(pin, value):
    strip.brightnes = float(value[0])

@blynk.handle_event("write V" + str(ON_OFF_VPIN))
def write_handler(pin, value):
    if int(value[0]) == 1:
        strip.on()
    else:
        strip.off()


blynk.run()
blynk.virtual_sync(COLOR_VPIN)
blynk.virtual_sync(BRIGHTNESS_VPIN)
blynk.virtual_sync(ON_OFF_VPIN)
blynk.run()

while True:
    blynk.run()
