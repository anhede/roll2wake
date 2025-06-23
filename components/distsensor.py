from components.hcsr04 import HCSR04
import time

CLOSE_THRESHOLD_CM = 20  # Default threshold for close distance in centimeters


class Distsensor(HCSR04):
    """
    A high-level class to handle the HC-SR04 ultrasonic distance sensor.
    Inherits from HCSR04 and provides user-friendly methods.
    Implements a caching and a minimum pulse delay to avoid rapid consecutive
    measurements which may return faulty values and waste power on double checks.
    """

    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500 * 2 * 30):
        super().__init__(trigger_pin, echo_pin, echo_timeout_us)
        self.min_pulse_delay_ms = 10  # Minimum delay between pulses in milliseconds
        self.last_pulse_time = 0
        self.last_distance_mm = 0

    def distance_mm(self):
        if abs(time.ticks_ms() - self.last_pulse_time) < self.min_pulse_delay_ms:
            # If the last pulse was too recent, return the last value
            return self.last_distance_mm
        else:
            # Send a new pulse and calculate the distance
            self.last_pulse_time = time.ticks_ms()
            self.last_distance_mm = super().distance_mm()

        return self.last_distance_mm

    def distance_cm(self):
        return self.distance_mm() / 10.0

    def is_close(self):
        """
        Check if the sensor detects an object within a close distance.
        """
        return self.distance_cm() <= CLOSE_THRESHOLD_CM


if __name__ == "__main__":
    # Example usage of the HCSR04 class
    sensor = Distsensor(trigger_pin=7, echo_pin=6)  # Adjust pins as needed

    while True:
        distance_cm = sensor.distance_cm()
        print(
            f"{'close' if sensor.is_close() else 'far':6} at {distance_cm:6.2f} cm",
            end="\t\r",
        )

        time.sleep_ms(50)  # Wait for 1 second before the next measurement
