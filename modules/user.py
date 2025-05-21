import sqlite3, json

def bool_readable(value: bool):
    if value: return "有効"
    else: return "無効"

class UserManager():
    def __init__(self):
        self.default_dict = {
            "voice": "gTTS:0"
        }

    def is_registered(self, user_id: int) -> bool:
        conn = sqlite3.connect("./users.db")
        cur = conn.cursor()

        cur.execute("SELECT data FROM user_settings WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return True
        else:
            return False

    def voice_value(self, user_id: int) -> dict:
        conn = sqlite3.connect("./users.db")
        cur = conn.cursor()

        cur.execute("SELECT data FROM user_settings WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            settings = json.loads(row[0])
        else:
            settings = self.default_dict

        return settings['voice']

    def load(self, user_id: int) -> dict:
        conn = sqlite3.connect("./users.db")
        cur = conn.cursor()

        cur.execute("SELECT data FROM user_settings WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            settings = json.loads(row[0])
        else:
            settings = self.default_dict

        return settings

    def write(self, user_id: int, data: dict):
        conn = sqlite3.connect("./users.db")
        cur = conn.cursor()

        json_data = json.dumps(data)
        cur.execute("""
            INSERT INTO user_settings (user_id, data)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET data=excluded.data
        """, (user_id, json_data))
        conn.commit()
        conn.close()
        return True

    def read(self, user_id: int) -> str:
        conn = sqlite3.connect("./users.db")
        cur = conn.cursor()

        cur.execute("SELECT data FROM user_settings WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            settings = json.loads(row[0])
        else:
            settings = self.default_dict

        value_text = ""
        for key in settings:
            match key:
                case "voice": 
                    value_text += f"現在の音声: {settings[key]}\n"
                case _: 
                    pass
        return value_text

    def update(self, user_id: int, updates: dict):
        current_data = self.load(user_id)
        current_data.update(updates)
        self.write(user_id, current_data)
        return True