from discord.ext import commands
import discord, json, os, re, asyncio, traceback, requests, subprocess
from gtts import gTTS
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
prefix = os.getenv("PREFIX")

with open(f"./tts_uri.json", "r") as f:
    URIS = json.load(f)
    f.close()

VOICEVOX_URI = URIS['VOICEVOX']
COEIROINK_URI = URIS['COEIROINK']

# Local Module
from modules.guild import GuildManager
from modules.user import UserManager
from modules.errors import play_error
from modules.sound_ex import convert_mp3_to_wav
from modules.channels import ChannelManager
from modules.coeiroink import convert_speaker_id_to_uuid

class MessageData():
    def __init__(self, 
                    content: str, 
                    author: discord.User, 
                    channel: discord.TextChannel, 
                    attachments: list, 
                    guild: discord.Guild
                ):
        self.content = content
        self.author = author
        self.channel = channel
        self.attachments = attachments
        self.guild = guild

class TextToSpeach(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = int(os.getenv("ERROR_CHANNEL"))
        self.messages = defaultdict(dict)
        self.reading = defaultdict(dict)

    async def tts(self, guild: discord.Guild):
        voice = discord.utils.get(self.bot.voice_clients, guild = guild)
        gm = GuildManager()
        um = UserManager()

        while len(self.messages[str(guild.id)]) != 0:
            if voice.is_playing():
                await asyncio.sleep(.5)

            else:
                try:
                    message = self.messages[str(guild.id)].pop(0)
                    self.reading[str(guild.id)] = message

                except discord.ClientException:
                    e = await play_error(message, f"ClientException: {traceback.format_exc()}")
                    if self.error_channel is not None:
                        channel = self.bot.get_channel(self.error_channel)
                        await self.error_channel.send(embed = e)
                    continue

                except:
                    e = await play_error(message, f"Exception: {traceback.format_exc()}")
                    if self.error_channel is not None:
                        channel = self.bot.get_channel(self.error_channel)
                        await self.error_channel.send(embed = e)
                    continue

                guild_settings = gm.setting_value(guild.id)
                if "vc_only_user" in guild_settings:
                    vc_only_user = guild_settings['vc_only_user']
                else:
                    vc_only_user = False

                if message.content == "" and len(message.attachments) == 0:
                    return
                elif vc_only_user == True and message.author not in voice.channel.members and type(message) != MessageData:
                    return

                else:
                    up = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
                    url_list = re.findall(up, message.content)
                    for url in url_list:
                        message.content = message.content.replace(url, "URL")

                    message.content = re.sub('```.*?```|`.*?`', 'コードブロック', message.content, flags = re.DOTALL)

                    if "～" in message.content:
                        message.content = message.content.replace("～", "ー")

                    if "〜" in message.content:
                        message.content = message.content.replace("〜", "ー")

                    if "^" in message.content:
                        message.content = message.content.replace("^", "")

                    if "＾" in message.content:
                        message.content = message.content.replace("＾", "")

                    if "\n" in message.content:
                        message.content = message.content.replace("\n", "、")

                    pattern = r'<@!?(\d+)>'
                    match = re.findall(pattern, message.content)
                    for user_id in match:
                        user = await message.guild.fetch_member(user_id)
                        
                        if guild_settings['vc_nickname'] == True:
                            user_name = f'、{user.display_name}、'
                        
                        else:
                            user_name = f"、{user.name}、"

                        message.content = re.sub(rf'<@!?{user_id}>', user_name, message.content)

                    pattern = r'<@&(\d+)>'
                    match = re.findall(pattern, message.content)
                    for role_id in match:
                        role = message.guild.get_role(int(role_id))
                        role_name = f'、{role.name}、'
                        message.content = re.sub(f'<@&{role_id}>', role_name, message.content)

                    pattern = r'\|{2}.+?\|{2}'
                    message.content = re.sub(pattern, '伏せ字', message.content)

                    pattern = r'<#?(\d+)>'
                    match = re.findall(pattern, message.content)
                    for channel_id in match:
                        channel = await message.guild.fetch_channel(channel_id)
                        channel_name = f'、{channel.name}、'
                        message.content = re.sub(rf'<#?{channel_id}>', channel_name, message.content)

                    _v = False
                    _p = ""
                    if message.content[-1:] == 'w' or message.content[-1:] == 'W' or message.content[-1:] == 'ｗ' or message.content[-1:] == 'W':
                        while message.content[-2:-1] == 'w' or message.content[-2:-1] == 'W' or message.content[-2:-1] == 'ｗ' or message.content[-2:-1] == 'W':
                            if _v:
                                message.content = message.content[:-1]
                            else:
                                _p = f"ワラ"
                                _v = True
                        message.content = message.content[:-1] + f'、ワラ{_p} '

                    if os.path.isfile(f"/disk1/YomiCanary/words/{message.guild.id}.json") is True:
                        with open(f"/disk1/YomiCanary/words/{message.guild.id}.json", "r") as f:
                            words = json.load(f)
                            f.close()
                        for w in list(words.keys()):
                            if w in message.content:
                                message.content = message.content.replace(w, words[w])

                    pattern = r'<:([a-zA-Z0-9_]+):\d+>'
                    match = re.findall(pattern, message.content)
                    for emoji_name in match:
                        emoji_read_name = emoji_name.replace('_', ' ')
                        message.content = re.sub(rf'<:{emoji_name}:\d+>', f'、{emoji_read_name}、', message.content)
                    pattern = r'<a:([a-zA-Z0-9_]+):\d+>'
                    match = re.findall(pattern, message.content)
                    for emoji_name in match:
                        emoji_read_name = emoji_name.replace('_', ' ')
                        message.content = re.sub(rf'<:{emoji_name}:\d+>', f'、{emoji_read_name}、', message.content)

                    if len(message.content) > 100:
                        message.content = message.content[:100] + "以下略"

                    if len(message.attachments) != 0 and guild_settings['vc_attachments'] == True:
                        message.content = message.content + "、ファイルが送信されました"

                    user_voice = um.voice_value(message.author.id)
                    sound_path = await self.read_text(message.content, user_voice, message.guild.id)

                    if type(sound_path) == discord.Embed:
                        if self.error_channel is not None:
                            channel = self.bot.get_channel(self.error_channel)
                            await channel.send(embed = sound_path)
                        continue

                    audio = discord.FFmpegPCMAudio(sound_path, options = "-loglevel error")
                    voice.play(audio)
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 1

                    self.reading[str(guild.id)] = {}

                    # --- Logs ---

    async def read_text(self, text: str, voice: str, guild_id: int):
        if voice == "gTTS:0":
            try:
                tts = gTTS(text, lang = 'ja', slow = False)
                tts.save(f"./tts/{guild_id}.mp3")
                sound_path = convert_mp3_to_wav(f"./tts/{guild_id}.mp3")
                return sound_path
            except Exception as exc:
                e = discord.Embed(
                    title = "読み上げエラー",
                    description = f"gTTSでの音声合成中にエラーが発生しました： ```py\n{exc}```",
                    color = discord.Color.red()
                )
                return e

        elif voice.startswith("voicevox:"):
            speaker_id = voice[len(f"voicevox:"):]

            header = {
                "Content-Type": "application/json"
            }
            audio_query = requests.post(url = f"{VOICEVOX_URI}/audio_query?text={text}&speaker={speaker_id}", 
                                        headers = header)
            if audio_query.status_code != 200: 
                e = discord.Embed(
                    title = "読み上げエラー", 
                    description = f"Audio Queryの取得中にエラーが発生しました： {audio_query.status_code}", 
                    color = discord.Color.red()
                )
                e.add_field(
                    name = f"エラー", 
                    value = f"```py\n{audio_query.text}```",
                    inline = False
                )
                e.add_field(
                    name = f"音声ID", 
                    value = f"{speaker_id}",
                    inline = False
                )
                e.add_field(
                    name = f"メッセージ内容", 
                    value = f"{text}",
                    inline = False
                )
                e.set_footer(
                    text = f"Error: VOICEVOX"
                )
                return e

            else: aq = audio_query.json()

            synthesis = requests.post(url = f"{VOICEVOX_URI}/synthesis?speaker={speaker_id}", 
                                        headers = header, json = aq)
            if synthesis.status_code != 200: 
                e = discord.Embed(
                    title = "読み上げエラー", 
                    description = f"Synthesisの作成中にエラーが発生しました： {audio_query.status_code}", 
                    color = discord.Color.red()
                )
                e.add_field(
                    name = f"エラー", 
                    value = f"```py\n{audio_query.text}```",
                    inline = False
                )
                e.add_field(
                    name = f"音声ID", 
                    value = f"{speaker_id}",
                    inline = False
                )
                e.add_field(
                    name = f"メッセージ内容", 
                    value = f"{text}",
                    inline = False
                )
                e.set_footer(
                    text = f"Error: VOICEVOX"
                )
                return e
            else: 
                with open(f"./tts/{guild_id}.wav", "wb") as f:
                    f.write(synthesis.content)
                    f.close()

            return f"./tts/{guild_id}.wav"

        elif voice.startswith("coeiroink:"):
            speaker_id = voice[len(f"coeiroink:"):]

            try:
                speaker_uuid = await convert_speaker_id_to_uuid(int(speaker_id))
            except:
                e = discord.Embed(
                    title = "読み上げエラー",
                    description = f"Speaker IDの変換中にエラーが発生しました： ```py\n{traceback.format_exc()}```",
                    color = discord.Color.red()
                )
                return e

            query = {
                "speakerUuid": speaker_uuid,
                "styleId": int(speaker_id),
                "text": text,
                "speedScale": 1.0,
                "volumeScale": 1.0,
                "prosodyDetail": [],
                "pitchScale": 0.0,
                "intonationScale": 1.0,
                "prePhonemeLength": 0.1,
                "postPhonemeLength": 0.5,
                "outputSamplingRate": 24000,
            }

            response = requests.post(
                url = f"{COEIROINK_URI}/v1/synthesis",
                headers={"Content-Type": "application/json"},
                data=json.dumps(query),
            )

            if response.status_code != 200: 
                e = discord.Embed(
                    title = "読み上げエラー",
                    description = f"音声合成中にエラーが発生しました： {response.status_code}",
                    color = discord.Color.red()
                )
                e.add_field(
                    name = f"エラー",
                    value = f"```py\n{response.text}```",
                    inline = False
                )
                e.add_field(
                    name = f"音声ID",
                    value = f"{speaker_id}",
                    inline = False
                )
                e.add_field(
                    name = f"メッセージ内容",
                    value = f"{text}",
                    inline = False
                )
                e.set_footer(
                    text = f"Error: COEIROINK"
                )
                return e
            else:
                with open(f"./tts/{guild_id}.wav", "wb") as f:
                    f.write(response.content)
                    f.close()

                return f"./tts/{guild_id}.wav"

        elif voice.startswith("ojtalk:"):
            name = voice[len(f"ojtalk:"):]
            path = f"./tts/{guild_id}.wav"
            sps = name.split("_")
            chara = sps[0]
            cmd = [
                "open_jtalk",
                "-x", "/var/lib/mecab/dic/open-jtalk/naist-jdic",
                "-m", f"/usr/share/hts-voice/{chara}/{name}.htsvoice",
                "-r", "1.0",
                "-ow", path
            ]
            res = subprocess.Popen(cmd, stdin = subprocess.PIPE)
            res.stdin.write(text.encode())
            res.stdin.close()
            res.wait()

            return f"./tts/{guild_id}.wav"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        else:
            voice = discord.utils.get(self.bot.voice_clients, guild = message.guild)
            if voice is None: return

            cm = ChannelManager()
            if cm.get_text_id(voice.channel.id) is None or cm.get_text_id(voice.channel.id) != message.channel.id:
                return

            if message.content == ";" or message.content == "；":
                voice.stop()
                return

            elif message.content.startswith(";") or message.content.startswith("；") or message.content.lower().startswith(prefix):
                return

            if str(message.guild.id) not in self.messages: self.messages[str(message.guild.id)] = []

            self.messages[str(message.guild.id)].append(
                MessageData(
                    content = message.content,
                    author = message.author,
                    channel = message.channel,
                    attachments = message.attachments,
                    guild = message.guild
                )
            )

            await self.tts(message.guild)

def setup(bot):
    bot.add_cog(TextToSpeach(bot))