# db.py
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from stats import Statistics

class StatisticsDB:
    def __init__(self, db_path: str = "stats.db"):
        self.db_path = db_path
        self._ensure_table()

    def _get_conn(self):
        # allow usage from multiple threads (flask + dash)
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _ensure_table(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def insert(self, stat: Statistics):
        """
        Persist a Statistics object into the DB.
        """
        ts = stat.timestamp
        if isinstance(ts, str):
            # try to parse isoformat, fallback to now()
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.utcnow()
        conn = self._get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT INTO statistics (type, value, timestamp) VALUES (?, ?, ?)",
            (stat.type, stat.value, ts.isoformat())
        )
        conn.commit()
        conn.close()

    def query(
        self,
        stat_type: Optional[str] = None,
        start: Optional[datetime]   = None,
        end:   Optional[datetime]   = None
    ) -> List[Statistics]:
        """
        Fetch statistics, optionally filtered by type and/or time window.
        """
        conn = self._get_conn()
        c = conn.cursor()

        clauses: List[str] = []
        params: List = []

        if stat_type:
            clauses.append("type = ?")
            params.append(stat_type)
        if start:
            clauses.append("timestamp >= ?")
            params.append(start.isoformat())
        if end:
            clauses.append("timestamp <= ?")
            params.append(end.isoformat())

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        c.execute(f"""
            SELECT type, value, timestamp
              FROM statistics
            {where}
            ORDER BY timestamp ASC
        """, params)

        rows = c.fetchall()
        conn.close()

        stats: List[Statistics] = []
        for t, v, ts in rows:
            stat = Statistics(stat_type=t, value=v, timestamp=ts)
            stats.append(stat)
        return stats
