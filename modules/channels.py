import sqlite3

class ChannelManager():
    def __init__(self):
        return

    def register_voices(self, voice_id: int, text_id: int):
        conn = sqlite3.connect(f"./voices.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO voices (voice, text)
            VALUES (?, ?)
            ON CONFLICT(voice) DO UPDATE SET text = excluded.text
        """, (voice_id, text_id))
        conn.commit()
        conn.close()
        return True

    def get_text_id(self, voice_id: int):
        conn = sqlite3.connect(f"./voices.db")
        cur = conn.cursor()
        cur.execute("SELECT text FROM voices WHERE voice = ?", (voice_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def get_voice_id(self, text_id: int):
        conn = sqlite3.connect(f"./voices.db")
        cur = conn.cursor()
        cur.execute("SELECT voice FROM voices WHERE text = ?", (text_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def delete_voice(self, voice_id: int):
        conn = sqlite3.connect(f"./voices.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM voices WHERE voice = ?", (voice_id,))
        conn.commit()
        conn.close()
        return True