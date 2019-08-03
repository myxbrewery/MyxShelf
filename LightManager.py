import time
from neopixel import *
from utils import threaded
import argparse

class LightManager:
    def __init__(self):
        LED_COUNT      = 52      # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        self.strip = Adafruit_NeoPixel(
            LED_COUNT, 
            LED_PIN, 
            LED_FREQ_HZ, 
            LED_DMA, 
            LED_INVERT, 
            LED_BRIGHTNESS, 
            LED_CHANNEL
        )
        # Color library is G, R, B
        self.load_color = Color(255, 193, 10)
        self.withdraw_color = Color(193, 255, 10)
        self.mode = "Idle"
        self.colorManager()
    
    @threaded
    def colorManager(self):
        self.mode_fn_mapping = {
            'Idle': self.idle,
            'Depositing': self.depositing,
            'Deposited': self.deposited,
            'Withdrawing': self.withdrawing,
            'Withdrawed': self.withdrawed,
        }
        while True:
            self.mode_fn_mapping[self.mode]()

    def idle(self):
        self.rainbowCycle(self.strip)

    def withdrawing(self):
        self.colorOscillate(self.strip, self.load_color, 30)
    
    def withdrawed(self):
        self.colorWipe(self.strip, self.load_color, 30)

    def depositing(self):
        self.colorOscillate(self.strip, self.deposit_color, 30)
    
    def deposited(self):
        self.colorWipe(self.strip, self.deposit_color, 30)

    def colorWipe(self, strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

    def colorOscillate(self, strip, color, wait_ms = 50):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            n = i - 20
            if(n < 0):
                n += strip.numPixels()
            strip.setPixelColor(n, Color(0, 0, 0))
            time.sleep(wait_ms/1000)
            strip.show()

    def theaterChase(self, strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)
    
    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def rainbow(self, strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
    
    def rainbowCycle(self, strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
    
    def theaterChaseRainbow(self, strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)

    def progressBar(self, color, total_duration):
        for i in range(0, strip.numPixels()):
            strip.setPixelColor(0, (0, 0, 0))
