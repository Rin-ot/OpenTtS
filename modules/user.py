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