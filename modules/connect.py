from gtts import gTTS
import discord

# Local Module
from modules.sound_ex import convert_mp3_to_wav

async def connect_sound(guild_id: int, voice: discord.VoiceClient):
    tts = gTTS("接続しました。", lang = 'ja', slow = False)
    tts.save(f"./tts/{guild_id}.mp3")
    sound_path = convert_mp3_to_wav(f"./tts/{guild_id}.mp3")
    audio = discord.FFmpegPCMAudio(sound_path, options = "-loglevel error")
    voice.play(audio)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 1
