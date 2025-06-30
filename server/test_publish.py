import requests
from datetime import datetime, timedelta
from random import randint
from stats import Statistics, STAT_INTERACTION, STAT_WAKEUP

monday = datetime(2025, 6, 24, 8, 0, 0)

SERVER_URL = "http://127.0.0.1:5000/stats"

def publish_stat(stat: Statistics):
    payload = {"type": stat.type, "value": stat.value}
    if stat.timestamp:
        payload["timestamp"] = stat.timestamp
    try:
        resp = requests.post(SERVER_URL, json=payload)
        print(f"POST {payload} -> {resp.status_code}: {resp.json()}")
    except Exception as e:
        print(f"Error posting {payload}: {e}")

if __name__ == "__main__":
    # Generate and publish sample data    # Example 7 day schedule

    # For 7 days
    now = monday
    for i in range(7):

        # Late night interactions
        slept_for = timedelta(hours=randint(6, 9))
        went_to_bed = now - slept_for
        for _ in range(randint(1, 5)):
            random_offset = timedelta(minutes=randint(0, 59))
            stat = Statistics(
                stat_type=STAT_INTERACTION,
                value=0, # Interaction has no value
                timestamp=(went_to_bed + random_offset).isoformat() # type: ignore
            )
            publish_stat(stat)
            

        # Wake up
        random_offset = timedelta(minutes=randint(0, 59))
        alarm_time_s = randint(0, 60)
        stat = Statistics(
            stat_type=STAT_WAKEUP,
            value=alarm_time_s,
            timestamp=(now + random_offset).isoformat()
        )
        publish_stat(stat)
        now += timedelta(days=1)
