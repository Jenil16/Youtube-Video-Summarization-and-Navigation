# Our Final Year Project
from flask import Flask, render_template, request
from flask import Flask, request, jsonify
import re
import os
import threading
from pytube import YouTube
import moviepy.editor as mp
import assemblyai as aai
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import math
import nltk
nltk.download('punkt')

app = Flask(__name__)


# Initializing the global variable
output_text = None
video_url = None
time = 0
subtopic = None
video_id = None
onComplete = 0
transcript = None


# All the routes are below here

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_video', methods=['POST'])
def add_video():
    global video_url
    global video_id
    video_url = request.form['videoUrl']
    video_id = get_youtube_id(video_url)
    video_title = get_video_title(video_url)

    if video_id:

        vurl = "https://www.youtube.com/embed/" + video_id
        save_path = "./video_audio_files"
        # video_title = get_video_title(video_url)
        video_file_name = f"{video_id}.mp4"
        # audio_file_name = f"{video_id}.wav"

        if file_exists_in_folder("./video_audio_files", video_id+".mp4"):
            return render_template('video_page.html', video_url = vurl)
              
        threading.Thread(target=download_video, args=(video_url, save_path, video_id)).start()
        # download_video(video_url, save_path, video_id)
        # video_path = f"{save_path}/{video_file_name}"
        # audio_path = f"{save_path}/{audio_file_name}"
        # convert_video_to_audio(video_path, audio_path)
        return render_template('video_page.html', video_url = vurl)
    else:
        return 'Please enter a valid YouTube video URL.'
    

@app.route('/check_download_status')
def check_download_status():
    global onComplete
    global video_id

    if file_exists_in_folder("./video_audio_files", video_id+".mp4"):
        onComplete = 1

    return jsonify({'onComplete': onComplete})


@app.route('/translate', methods=['GET','POST'])
def translate():
    # global video_url
    global output_text
    global video_id
    global transcript
 
    if output_text is None:
        transcript = get_transcript(video_id)
        output_text = transcript.text
        return render_template("translate.html" , output_text=output_text)    
    else:
        return render_template("translate.html" , output_text=output_text)


@app.route('/summary', methods=['GET','POST'])
def summary():
    global output_text
    global video_id
    global transcript
    
    if output_text is None:
        transcript = get_transcript(video_id)
        output_text = transcript.text
    
    s = output_text.split(".")
    l = len(s)
    n = math.ceil(l * 0.33)
    summary = summarize_text(output_text, n)
    return render_template("summary.html", summarized_text=summary)


@app.route('/subtopic_skip', methods=['GET','POST'])
def subtopic_skip():
    global video_id
    global transcript
      
    if file_exists_in_folder("./video_audio_files", video_id+".srt"):
        return render_template("subtopic_skip.html")

    # Building srt file
    if transcript is None:
        transcript = get_transcript(video_id)
        
    subtitles = transcript.export_subtitles_srt()
    f = open("./video_audio_files/"+video_id+".srt", "a")
    f.write(subtitles)
    f.close()
    return render_template("subtopic_skip.html")
    

@app.route('/video_skip', methods=['POST','GET'])
def video_skip():
    global time
    global subtopic
    global video_id
    
    # time = 0
    subtitles = parse_srt("./video_audio_files/"+video_id+".srt")
    subtopic = request.form['subtopic']
    timestamp = find_subtitle_containing_text(subtitles, subtopic)
    if timestamp is not None:
        time = timestamp
    else:
        print('Subtopic not found in subtitles')

    return render_template("video_skip.html", time = time, video_id = video_id)



# All the functions are below here
    
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

#function is used to download video
def download_video(url, save_path, video_id):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4', resolution='360p').first()  # Get the highest resolution MP4 stream
    file_name = f"{video_id}.mp4"
    stream.download(output_path=save_path, filename=file_name)
    print("Download completed.")

#funtion is used to convert video to audio
# def convert_video_to_audio(video_path, audio_path):
#     video = mp.VideoFileClip(video_path)
#     audio = video.audio
#     audio.write_audiofile(audio_path)
#     print("Conversion completed.")


def get_transcript(video_id):
    aai.settings.api_key = "7e2a126b073a4d4da1312644f147ad47"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("./video_audio_files/"+video_id+".mp4")
    return transcript


def summarize_text(text, num_sentences):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)


def parse_srt(file_path):
    subtitles = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    current_subtitle = None
    for line in lines:
        if current_subtitle is None:
            current_subtitle = {'index': int(line.strip())}
        elif not line.strip():
            subtitles.append(current_subtitle)
            current_subtitle = None
        elif '-->' in line:
            start, end = line.strip().split('-->')
            current_subtitle['start'] = parse_time(start.strip())
            current_subtitle['end'] = parse_time(end.strip())
        else:
            current_subtitle.setdefault('text', []).append(line.strip())
    return subtitles


def parse_time(time_str):
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2].replace(',', '.'))
    return hours * 3600 + minutes * 60 + seconds


def find_subtitle_containing_text(subtitles, subtopic):
    for subtitle in subtitles:
        if subtopic.lower() in ' '.join(subtitle['text']).lower():
            return subtitle['start']
    return None


def file_exists_in_folder(folder_path, filename):
    # Get list of files in the folder
    files = os.listdir(folder_path)
    # Check if the filename exists in the list of files
    return filename in files



# Main method

if __name__ == '__main__':
    app.run(debug=True)
