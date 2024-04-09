import base64
import numpy as np
from scipy.io.wavfile import write
import requests

def get_headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

def get_audio(file_path, target_lang, source_lang, out_path):
    url = "https://seamless_api.metademolab.com/predict_expressivity"
    with open(file_path, 'rb') as file:
        files = {
            'body': (file_path.split('/')[-1], file, 'audio/wav'),
            'target_lang': (None, target_lang),
            'source_lang': (None, source_lang),
        }
        res = requests.post(url, files=files, headers=get_headers(), verify=False)
    
    if res.status_code == 200:
        o = res.json()
        decoded_data = base64.b64decode(o["wav"])
        audio_array = np.frombuffer(decoded_data, dtype=np.float32)
        output_file_path = out_path
        write(output_file_path, 24000, audio_array)
        print(f"WAV file has been created: {output_file_path}")
    else:
        print(f"Error: {res.status_code}")

if __name__ == "__main__":
    get_audio(
        file_path="test.wav",
        target_lang="de",
        source_lang="en"
    )