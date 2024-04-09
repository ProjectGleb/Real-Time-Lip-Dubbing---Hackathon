from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from speech_backend_py import get_audio
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
from moviepy.audio.AudioClip import AudioClip
import logging
import moviepy
import time

logging.basicConfig(level=logging.INFO)  # or use your desired logging level

app = FastAPI()

VIDEO_PATH = ".\\temp_videos\\blob.mp4"
AUDIO_PATH = ".\\temp_videos\\blob.wav"
OUT_PATH   = ".\\temp_videos\\out.mp4"
PRED_PATH  = ".\\temp_videos\\pred.wav"

# Setup CORS (Cross-Origin Resource Sharing) to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def extract_audio(path):
    print('a')

    moviepy.video.io.ffmpeg_tools.ffmpeg_extract_audio(VIDEO_PATH, AUDIO_PATH)


def gen_video_new(video_path, audio_path, output):
    moviepy.video.io.ffmpeg_tools.ffmpeg_merge_video_audio(video_path, audio_path, output)


@app.post("/translate")
async def translate(video: UploadFile = File(...)):
    
    time.sleep(1)

    # 1. Get video
    with open(VIDEO_PATH, "wb+") as file_object:
        file_object.write(video.file.read())

    print("video saved")

    # 2. Extract audio
    extract_audio(VIDEO_PATH)

    print("extracted audio")

    # 3. Generate translated audio using SeamlessExpressive
    get_audio(
        file_path=AUDIO_PATH,
        target_lang="es",
        source_lang="en",
        out_path=PRED_PATH
    )

    print("meta api worked")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)