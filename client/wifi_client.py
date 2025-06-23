import network
import time
import ntptime
from machine import RTC


class WifiClient:
    def __init__(self, timeout: int = 60):
        try:
            with open("/client/wifi_settings.txt") as f:
                line = f.readline().strip()
                ssid, password = line.split(",", 1)
        except:
            print("WiFi settings file invalid or not found. Please create /client/wifi-settings.txt with 'ssid,password'.")
            return
        self.ssid = ssid
        self.password = password
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(True)
        self.timeout = timeout
        self.connect()
        self.set_swedish_time()

    def connect(self):
        self.sta_if.connect(self.ssid, self.password)
        start_time = time.time()
        attempts = 0
        while not self.sta_if.isconnected() and time.time() - start_time < self.timeout:
            attempts += 1
            print(f"Attempt {attempts} to connect to WiFi")
            time.sleep_ms(1000)   
        if self.sta_if.isconnected():
            print("Connected to WiFi")
            print(self.sta_if.ifconfig())
        else:
            print("Failed to connect to WiFi")


    def set_swedish_time(self):
        """
        Sync the Pico W RTC to Swedish local time (CET/CEST) via NTP.
        """
        # 1. Sync RTC to UTC
        ntptime.settime()

        # 2. Current UTC as seconds since epoch
        t = time.time()

        # 3. Compute DST transition times (01:00 UTC on last Sundays)
        year = time.localtime(t)[0]
        # Last Sunday of March
        dst_start = time.mktime((
            year, 3,
            31 - ((5 * year // 4 + 4) % 7),
            1, 0, 0,
            0, 0, 0
        ))
        # Last Sunday of October
        dst_end = time.mktime((
            year, 10,
            31 - ((5 * year // 4 + 1) % 7),
            1, 0, 0,
            0, 0, 0
        ))

        # 4. Pick the correct offset: 2 h in DST, else 1 h
        if dst_start <= t < dst_end:
            offset = 2 * 3600   # CEST
        else:
            offset = 1 * 3600   # CET

        # 5. Compute local time and update RTC
        tm = time.localtime(t + offset)
        rtc = RTC()
        # RTC.datetime expects (year, month, day, weekday, hour, minute, second, subseconds)
        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))

        # (Optional) Show what we’ve set
        print("Swedish local time:", tm)


if __name__ == "__main__":
    client = WifiClient()