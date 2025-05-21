import requests, json, traceback

with open(f"./tts_uri.json", "r") as f:
    URIS = json.load(f)
    f.close()

BASE_URI = URIS['COEIROINK']

async def convert_speaker_id_to_uuid(speaker_id: int) -> str:
    url = f"{BASE_URI}/v1/speakers_path_variant"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for speaker in data:
            for style in speaker['styles']:
                if style['styleId'] == speaker_id:
                    return speaker['speakerUuid']
    else:
        raise Exception(f"Error: {traceback.format_exc()}")