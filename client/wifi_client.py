import network
import time

class WifiClient:
    def __init__(self, ssid: str, password: str, timeout: int = 60):
        self.ssid = ssid
        self.password = password
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(True)
        self.timeout = timeout
        self.connect()

    def connect(self):
        self.sta_if.connect(self.ssid, self.password)
        start_time = time.time()
        attempts = 0
        while not self.sta_if.isconnected() and time.time() - start_time < self.timeout:
            attempts += 1
            print(f"Attempt {attempts} to connect to WiFi")
            time.sleep(1)   
        if self.sta_if.isconnected():
            print("Connected to WiFi")
            print(self.sta_if.ifconfig())
        else:
            print("Failed to connect to WiFi")

if __name__ == "__main__":
    with open("wifi-settings.txt", "r") as f:
        line = f.readline().strip()
        ssid, password = line.split(",", 1)
    client = WifiClient(ssid, password)