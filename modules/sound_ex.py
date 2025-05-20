import pydub, os

def convert_mp3_to_wav(mp3: str):
    wav_path = mp3.replace(".mp3", ".wav")
    audio = pydub.AudioSegment.from_mp3(mp3)
    audio.export(wav_path, format='wav')
    os.remove(mp3)
    return wav_path