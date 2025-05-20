import sqlite3, json

def bool_readable(value: bool):
    if value: return "有効"
    else: return "無効"

class GuildManager():
    def __init__(self):
        self.default_dict = {
                "read_user_join_leave": False,
                "read_attachment": False,
                "read_only_vc": False,
                "auto_connect": {
                    "enable": False,
                    "voice_channel": None,
                    "text_channel": None
                }
            }
        pass

    def is_registered(self, guild_id: int) -> bool:
        conn = sqlite3.connect("./guilds.db")
        cur = conn.cursor()

        cur.execute("SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cur.fetchone()
        if row:
            return True
        else:
            return False

    def setting_value(self, guild_id: int) -> dict:
        conn = sqlite3.connect("./guilds.db")
        cur = conn.cursor()

        cur.execute("SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cur.fetchone()
        if row:
            settings = json.loads(row[0])
        else:
            settings = self.default_dict

        return settings

    def read(self, guild_id: int) -> str:
        conn = sqlite3.connect("./guilds.db")
        cur = conn.cursor()

        cur.execute("SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cur.fetchone()
        if row:
            settings = json.loads(row[0])
        else:
            settings = self.default_dict

        value_text = ""
        for key in settings:
            match key:
                case "read_user_join_leave": 
                    value_text += f"ユーザーが接続/切断したときに読み上げる: {bool_readable(settings[key])}\n"
                case "read_attachment": 
                    value_text += f"メッセージの添付ファイルを読み上げる: {bool_readable(settings[key])}\n"
                case "read_only_vc":
                    value_text += f"ボイスチャンネルにいるユーザーのみ読み上げる: {bool_readable(settings[key])}\n"
                case "auto_connect": 
                    if settings[key]['enable']: 
                        value_text += f"自動接続: {bool_readable(settings[key]['enable'])}\n- 接続チャンネル: {settings[key]['text_channel']} -> {settings[key]['voice_channel']}\n"
                    else:
                        value_text += f"自動接続: {bool_readable(settings[key]['enable'])}"
                case _:
                    pass

        return value_text