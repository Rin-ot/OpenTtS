import requests, json, subprocess, os

with open(f"./tts_uri.json", "r") as f:
    URIS = json.load(f)
    f.close()

VOICEVOX_URI = URIS['VOICEVOX']
COEIROINK_URI = URIS['COEIROINK']

async def voicevox_data():
    url = f"{VOICEVOX_URI}/speakers"
    req = requests.get(url = url)
    return (req.status_code, req.json())

async def get_voicevox_speaker(style_id: int):
    url = f"{VOICEVOX_URI}/speakers"
    req = requests.get(url = url)
    if req.status_code != 200: raise Exception(f"Error: {req.status_code}")
    else:
        for chara in req.json():
            for style in chara['styles']:
                if style['id'] == int(style_id):
                    return f"{chara['name']} - {style['name']}"

                else: continue
        else:
            return f"Unknown"

async def coeiroink_data():
    url = f"{COEIROINK_URI}/v1/speakers_path_variant"
    req = requests.get(url = url)
    return (req.status_code, req.json())

async def get_coeiroink_speaker(style_id: int):
    url = f"{COEIROINK_URI}/v1/speakers_path_variant"
    req = requests.get(url = url)
    if req.status_code != 200: raise Exception(f"Error: {req.status_code}")
    else:
        for chara in req.json():
            for style in chara['styles']:
                if style['styleId'] == int(style_id):
                    return f"{chara['speakerName']} - {style['styleName']}"

                else: continue
        else:
            return f"Unknown"

async def ojtalk_data():
    cmd = [
        "open_jtalk", "-h"
    ]
    try:
        subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        data = {}
        charas = os.listdir(f"/usr/share/hts-voice/")
        for chara in charas:
            data[f"{chara}"] = []
            voices = os.listdir(f"/usr/share/hts-voice/{chara}/")
            for voice in voices:
                if voice.endswith(".htsvoice"):
                    data[f"{chara}"].append(voice)

        return (200, data)

    except:
        return (400, {})