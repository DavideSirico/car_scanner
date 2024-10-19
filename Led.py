import threading
import time
from Logger import Logger
import gpiozero

logging = Logger()


class Led:
    def __init__(self, pin: int, color: str, intensity: float = 1):
        self.color = color
        self.led = gpiozero.PWMLED(pin)
        self.blinking = False
        self.thread = None
        self.lock = threading.Lock()  # Add a lock for thread-safety
        self.default_intensity = intensity

    def _blink(self, intensity=None):
        while True:
            with self.lock:
                if not self.blinking:
                    break  # Exit if blinking is stopped

            # Blink the LED
            logging.info(f"LED {self.color} is ON")

            if intensity is None:
                intensity = self.default_intensity
            self.led.value = intensity
            time.sleep(self.blink_interval)

            logging.info(f"LED {self.color} is OFF")

            self.led.off()
            time.sleep(self.blink_interval)

    def start_blinking(self, blink_interval: float = 0.5):
        with self.lock:
            if self.blinking:
                return  # Don't start a new thread if already blinking
            self.blinking = True
            self.blink_interval = blink_interval

        # get current state of the LED
        self.was_on = self.led.is_lit
        # Start the blinking in a separate thread
        self.thread = threading.Thread(target=self._blink)
        self.thread.start()

    def stop_blinking(self, intensity=None):
        with self.lock:
            if not self.blinking:
                return  # Already stopped, do nothing
            self.blinking = False

        # Wait for the blinking thread to finish
        if self.thread:
            self.thread.join()
            self.thread = None
            if self.was_on:
                if intensity is None:
                    intensity = self.default_intensity
                self.led.value = intensity
            else:
                self.led.off()

    def turn_on(self, intensity=None):
        with self.lock:
            if intensity is None:
                intensity = self.default_intensity
            self.led.value = intensity
            logging.info(f"LED {self.color} turned ON with intensity {intensity}")

    def turn_off(self):
        with self.lock:
            self.led.off()
            logging.info(f"LED {self.color} turned OFF")
