
from flask import Flask, render_template, request
import re
from pytube import YouTube
import moviepy.editor as mp

app = Flask(__name__)
video_url = ''  # Initialize the global variable

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_video', methods=['POST'])
def add_video():
    global video_url  # Use the global keyword to modify the global variable
    video_url = request.form['videoUrl']
    video_id = get_youtube_id(video_url)
    if video_id:
        embed_code = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        save_path = "./video_audio_files"
        video_title = get_video_title(video_url)
        video_file_name = f"{video_title}.mp4"
        audio_file_name = "audio.wav"

        download_video(video_url, save_path)

        video_path = f"{save_path}/{video_file_name}"
        audio_path = f"{save_path}/{audio_file_name}"

        convert_video_to_audio(video_path, audio_path)

        # return audio_path
        return embed_code
    else:
        return 'Please enter a valid YouTube video URL.'

    

def get_video_title(url):
    try:
        yt = YouTube(url)
        video_title = yt.title
        return video_title
    except Exception as e:
        print("Error:", e)
        return None

    
def get_youtube_id(url):
    # Regular expression to match YouTube video IDs in various URL formats
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"   
    match = re.search(regex, url)
    if match:
        return match.group(1)  # Return the video ID
    else:
        return None  # Return None if no match is found

def download_video(url, save_path):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4').first()  # Get the highest resolution MP4 stream
    stream.download(output_path=save_path)
    print("Download completed.")

def convert_video_to_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    print("Conversion completed.")


if __name__ == '__main__':
    app.run(debug=True)
