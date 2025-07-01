from datetime import datetime, time, timedelta, date
from bisect import bisect_left
from typing import List
from datetime import timezone

# define a simple record to hold each night’s data
class SleepRecord:
    def __init__(self, date: date, bedtime: datetime, wakeup: datetime, duration: timedelta):
        self.date = date
        self.bedtime: datetime = bedtime
        self.wakeup: datetime = wakeup
        self.duration: timedelta = duration

    def __iter__(self):
        return iter((self.date, self.bedtime, self.wakeup, self.duration))

    def __repr__(self):
        return (f"SleepRecord(date={self.date!r}, bedtime={self.bedtime!r}, "
                f"wakeup={self.wakeup!r}, duration={self.duration!r})")
    
def ensure_aware(dt):
    if dt.tzinfo is None:
        # assume naive timestamps are UTC; adjust if you need another zone
        return dt.replace(tzinfo=timezone(timedelta(hours=+2)))
    return dt

def infer_sleep_periods(
    interactions: List[datetime],
    wakeups: List[datetime],
    evening_start: time = time(18, 0)
) -> List[SleepRecord]:
    """
    Returns a list of SleepRecord(date, bedtime, wakeup, duration).
    Logic is:
      1) Sort interactions & wakeups.
      2) For each wakeup w on calendar‐date D:
         a) grab all interactions < w
         b) split into:
            • prev_evening: on D-1 with t >= evening_start
            • early_morning: on D
         c) if prev_evening: bedtime = latest(prev_evening)
            elif early_morning: bedtime = earliest(early_morning)
            else: skip
         d) duration = w - bedtime
      3) return a list of SleepRecords, sorted by date.
    """

    interactions = sorted(
        (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc))
        for dt in interactions
    )    
    wakeups = sorted(
        (ensure_aware(dt) if dt.tzinfo is None else dt)
        for dt in wakeups
    )
    records = []
    seen_days = set()
    for w in wakeups:
        day = w.date()
        if day in seen_days:
            continue
        seen_days.add(day)

        idx = bisect_left(interactions, w)
        preceding = interactions[:idx]
        if not preceding:
            continue

        day       = w.date()
        yesterday = day - timedelta(days=1)

        prev_evening = [
            t for t in preceding
            if t.date() == yesterday and t.time() >= evening_start
        ]
        if prev_evening:
            bedtime = max(prev_evening)
        else:
            early_morning = [t for t in preceding if t.date() == day]
            if not early_morning:
                continue
            bedtime = min(early_morning)

        duration = w - bedtime
        records.append(SleepRecord(date=day,
                                   bedtime=bedtime,
                                   wakeup=w,
                                   duration=duration))

    return records



if __name__ == "__main__":
    from datetime import datetime

    interactions = [
        datetime(2025,6,24,22,0),
        datetime(2025,6,25, 3,0),
        datetime(2025,6,25,23,0),
        datetime(2025,6,26, 2,0),
    ]
    wakeups = [
        datetime(2025,6,25, 7,0),
        datetime(2025,6,26, 7,30),
    ]

    periods = infer_sleep_periods(interactions, wakeups)
    for rec in periods:
        print(f"{rec.date}: went to bed at {rec.bedtime.time()}, woke at {rec.wakeup.time()}, slept {rec.duration}")
