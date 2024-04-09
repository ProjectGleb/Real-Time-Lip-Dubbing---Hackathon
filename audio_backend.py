from fastapi import FastAPI, File, UploadFile, HTTPException
from pydub import AudioSegment
import os
from fastapi.middleware.cors import CORSMiddleware
from speech_backend_py import get_audio

import requests
import librosa
import librosa.display
import soundfile as sf




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/upload_audio/")
async def upload_audio(audio: UploadFile = File(...)):
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")

    filename, file_extension = os.path.splitext(audio.filename)
    if file_extension.lower() != '.wav':
        raise HTTPException(status_code=400, detail="Unsupported file format")

    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    with open(file_path, "wb") as f:
        f.write(await audio.read())



    audio_data, sample_rate = librosa.load('./uploads/recording.wav', sr=None)
    pcm_audio_data = (audio_data * 32767).astype('int16')
    sf.write('./uploads/output.wav', pcm_audio_data, sample_rate)



    get_audio(
        file_path='./uploads/output.wav',
        target_lang="es",
        source_lang="en",
        out_path='./uploads/translation.wav'
    )



    print('got audio')


    url = "http://192.9.245.237:8000/lips"

    payload = {}
    files=[
    ('audio',('translation.wav',open('uploads/translation.wav','rb'),'audio/wav'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    with open('may_translate.mp4', 'wb') as f:
        f.write(response.content)
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
