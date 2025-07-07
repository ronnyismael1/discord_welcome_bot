import sqlite3
import json
from datetime import datetime

class OnboardingDB:
    def __init__(self, db_path="data/onboarding.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS onboarding (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    channel_id TEXT,
                    channelname TEXT,
                    started_at TEXT,
                    status TEXT,
                    answers TEXT
                )
            """)

    def add_user(self, user_id, username, channel_id, channelname):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO onboarding (user_id, username, channel_id, channelname, started_at, status, answers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                channel_id,
                channelname,
                datetime.utcnow().isoformat(),
                "waiting",
                json.dumps({})
            ))

    def update_status(self, user_id, status):
        with self.conn:
            self.conn.execute("""
                UPDATE onboarding SET status=? WHERE user_id=?
            """, (status, user_id))

    def save_answers(self, user_id, answers_dict):
        with self.conn:
            self.conn.execute("""
                UPDATE onboarding SET answers=? WHERE user_id=?
            """, (json.dumps(answers_dict), user_id))

    def get_waiting_users(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM onboarding WHERE status='waiting'
        """)
        return cur.fetchall()

    def get_user(self, user_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM onboarding WHERE user_id=?
        """, (user_id,))
        return cur.fetchone()


    def get_answers(self, user_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT answers FROM onboarding WHERE user_id=?
        """, (user_id,))
        row = cur.fetchone()
        if row and row["answers"]:
            return json.loads(row["answers"])
        return {}


