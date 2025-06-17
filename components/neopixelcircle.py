from machine import Pin
import neopixel


class NeoPixelCircle:
    """
    A class to control an 8-LED NeoPixel RGB module.
    """

    def __init__(self, pin: int, brightness: float = 1.0):
        self.pin = Pin(pin, Pin.OUT)
        self.np = neopixel.NeoPixel(self.pin, 8)
        self.brightness = max(0.0, min(1.0, brightness))
        self.clear()  # initialize with all LEDs off

    def set_colors(self, colors):
        """
        Set the strip to the given array of colors and immediately update.
        :param colors: list/tuple of length ≤ num_leds where each element is either:
            - an (r, g, b) tuple with 0-255 ints, or
            - a 0xRRGGBB integer.
        """
        for i in range(8):
            if i < len(colors):
                c = colors[i]
                # unpack integer or tuple
                if isinstance(c, int):
                    r = (c >> 16) & 0xFF
                    g = (c >> 8) & 0xFF
                    b = c & 0xFF
                else:
                    r, g, b = c
                # apply brightness
                r = int(r * self.brightness)
                g = int(g * self.brightness)
                b = int(b * self.brightness)
                self.np[i] = (r, g, b)
            else:
                # turn off any remaining LEDs
                self.np[i] = (0, 0, 0)
        self.np.write()
        self.state = colors  # store last state for potential future use

    def clear(self):
        """
        Turn all LEDs off.
        """
        self.set_colors([])

    def fill(self, color):
        """
        Fill the entire strip with one color.
        :param color: an (r, g, b) tuple or 0xRRGGBB int.
        """
        self.set_colors([color] * 8)

    def set_brightness(self, brightness):
        """
        Change the global brightness (0.0-1.0) and update current colors.
        """
        self.brightness = max(0.0, min(1.0, brightness))
        self.set_colors(self.state)


if __name__ == "__main__":
    import time
    from math import sin, pi

    # Example usage on GP0 with 8 LEDs
    strip = NeoPixelCircle(pin=16, brightness=0.1)

    # rainbow chase
    colors = [
        (255, 0, 0),  # red
        (255, 127, 0),  # orange
        (255, 255, 0),  # yellow
        (0, 255, 0),  # green
        (0, 0, 255),  # blue
        (75, 0, 130),  # indigo
        (148, 0, 211),  # violet
        (255, 255, 255),  # white
    ]

    while True:
        # shift the list by one each time
        strip.set_colors(colors)
        colors = colors[1:] + colors[:1]
        brightness = (sin(time.ticks_ms() / 1000 * pi) + 1) / 2  # oscillate brightness
        strip.set_brightness(brightness)
        time.sleep_ms(50)
