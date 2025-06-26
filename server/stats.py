# shared/statistics.py

# try MicroPython’s ujson first, otherwise stdlib json
try:
    import ujson as json
except ImportError:
    import json

STAT_INTERACTION = 'interaction' # Tracks any user interaction
STAT_WAKEUP = 'wakeup' # Wakeup event / Time to wake up

class Statistics:
    def __init__(self, stat_type: str, value: float, timestamp: str):
        # stat_type: string name of the metric
        # value: numeric (we’ll coerce to float)
        # timestamp: ISO8601 string (or anything serializable)
        self.type = stat_type
        self.value = value
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, data):
        # simple presence/type checks
        if 'type' not in data or 'value' not in data or 'timestamp' not in data:
            raise ValueError("Missing one of 'type', 'value', or 'timestamp'")
        # coerce value
        try:
            val = float(data['value'])
        except Exception:
            raise ValueError("'value' must be a number")
        return cls(data['type'], val, data['timestamp'])

    def to_dict(self):
        return {
            'type':      self.type,
            'value':     self.value,
            'timestamp': self.timestamp
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))

if __name__ == '__main__':
    # simple test
    stat = Statistics('test_stat', 42.0, '2023-10-01T12:00:00Z')
    print(stat.to_json())
    print(Statistics.from_json(stat.to_json()).to_dict())