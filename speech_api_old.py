from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from speech_backend_py import get_audio
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
from moviepy.audio.AudioClip import AudioClip
import logging
import moviepy

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
    #v = VideoFileClip(path)
    #a = v.audio
    #a.write_audiofile(AUDIO_PATH)
    moviepy.video.io.ffmpeg_tools.ffmpeg_extract_audio(VIDEO_PATH, AUDIO_PATH)


def gen_video_new(video_path, audio_path, output):
    moviepy.video.io.ffmpeg_tools.ffmpeg_merge_video_audio(video_path, audio_path, output)

def gen_video(video_path, audio_path):
    # Load the original video
    print('a')
    video = VideoFileClip(video_path)
    print('b')
    # Load the new audio (ensure it's the same duration as the video)
    new_audio = AudioFileClip(audio_path)

    duration_difference = video.duration - new_audio.duration
    if duration_difference > 0:
        # If the audio is shorter, pad it at the start with silence
        silence = AudioClip(lambda t: [0]*2, duration=duration_difference, fps=new_audio.fps)
        padded_audio = CompositeAudioClip([silence.set_start(0), new_audio.set_start(duration_difference)])
    elif duration_difference < 0:
        # If the audio is longer, truncate it to match the video duration
        padded_audio = new_audio.subclip(-duration_difference, new_audio.duration)
    else:
        # If they're the same duration, no need to adjust
        padded_audio = new_audio

    video = video.set_audio(padded_audio)

    # Export the video with the new audio
    with open("log.txt", "w+") as f:
        f.write(OUT_PATH + "\n")
    video.write_videofile(OUT_PATH, codec="libx264", audio_codec="aac")

@app.post("/translate")
async def translate(video: UploadFile = File(...)):
    
    try:
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

        # 4. Generate new video
        #gen_video_new(VIDEO_PATH, PRED_PATH, OUT_PATH)
        
        #print("stitching audio and video worked")

        #return {"filename": video.filename, "message": "Video successfully uploaded and saved."}
    except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)