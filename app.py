
from flask import Flask, render_template, request
import re
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
global video_url   # Initialize the global variable
global output_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['GET','POST'])
def translate():
    global video_url
    global output_text
    video_title = get_video_title(video_url)
    # x = video_title
    aai.settings.api_key = "7e2a126b073a4d4da1312644f147ad47"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("./video_audio_files/"+video_title+".mp4")
    # transcript = transcriber.transcribe("./my-local-audio-file.wav")
    subtitles = transcript.export_subtitles_srt()
    f = open("./video_audio_files/subtitles.srt", "a")
    f.write(subtitles)
    f.close()
    output_text = transcript.text
    # print(transcript.text)
    return render_template("translate.html" , output_text=output_text)

@app.route('/summary', methods=['GET','POST'])
def summary():
    global video_url
    video_title = get_video_title(video_url)
    # x = video_title
    aai.settings.api_key = "7e2a126b073a4d4da1312644f147ad47"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("./video_audio_files/"+video_title+".mp4")
    output_text = transcript.text
    s = output_text.split(".")
    l = len(s)
    n = math.ceil(l * 0.33)
    summary = summarize_text(output_text,n)
    return render_template("summary.html", summarized_text = summary)

@app.route('/subtopic_skip', methods=['GET','POST'])
def subtopic_skip():
    return render_template("subtopic_skip.html")


@app.route('/add_video', methods=['POST'])
def add_video():
    global video_url  # Use the global keyword to modify the global variable
    video_url = request.form['videoUrl']
    video_id = get_youtube_id(video_url)
    if video_id:
        vurl = "https://www.youtube.com/embed/" + video_id
        # embed_code = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        save_path = "./video_audio_files"
        video_title = get_video_title(video_url)
        video_file_name = f"{video_title}.mp4"
        audio_file_name = f"{video_title}.wav"

        download_video(video_url, save_path)

        video_path = f"{save_path}/{video_file_name}"
        audio_path = f"{save_path}/{audio_file_name}"

        convert_video_to_audio(video_path, audio_path)

        # return audio_path
        # return embed_code
        return render_template('video_page.html', video_url = vurl)
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

def summarize_text(text, num_sentences):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)


if __name__ == '__main__':
    app.run(debug=True)
