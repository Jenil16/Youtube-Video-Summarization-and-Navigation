# Our Final Year Project
from flask import Flask, render_template, request
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError

nltk.download('punkt')

app = Flask(__name__)


#Database configuration's
app.config['MYSQL_HOST'] = '152.58.63.97'
app.config['MYSQL_USER'] = 'admin'           
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'vsns_db'

#mysql object
mysql = MySQL(app)


# Initializing the global variable
output_text = None
video_url = None
time = 0
subtopic = None
video_id = None
onComplete = 0
transcript = None
subtitles = None


#Setup Server config
server_host = "smtp.gmail.com"
server_port = 587

#Setup Gmail credentials
my_email = ""
my_password = ""

#Sender and receiver email
sender = ""
receiver = None

#Setup Subject and to,from
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = "SignUp Successfull 😄"


# All the routes are below here

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('home.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.form['loginuseremail']
    password = request.form['loginuserpassword']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET Password=%s WHERE Email=%s", (password, email))
    mysql.connection.commit()
    cur.close()

    return render_template('login.html')



@app.route('/add_info',methods=['GET', 'POST'])
def add_info():
    signedup = False
    username = request.form['username']
    password = request.form['userpassword']
    number = request.form['usernumber']
    email = request.form['useremail']
    receiver = email
    
    try:
        v = validate_email(email)
        validated_email = v.email
        print(validated_email)
    except EmailNotValidError as e:
        print('Invalid Email address',e)
        InvalidEmail = True
        return render_template('index.html',InvalidEmail= InvalidEmail)
    else:
    
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (Username, Password, Mobile_no, Email) VALUES (%s, %s, %s, %s)", (username, password, number, email))
        mysql.connection.commit()
        cur.close()
        # print('another time',validated_email)
        
        signedup = True
        
        body = f"Hey {username} You are successfully signup \n Your Username is {username} \n  Your Number is {number} \n Your Password is {password}"
        msg.attach(MIMEText(body,'plain'))
        with smtplib.SMTP(server_host,server_port) as server_connection:
            server_connection.starttls()
            server_connection.login(user=my_email,password=my_password)
            text = msg.as_string()
            server_connection.sendmail(from_addr=sender,to_addrs=receiver,msg=text)
        return render_template('home.html', signedup = signedup,username=username)

@app.route('/verify_info', methods=['GET','POST'])
def verify_info():
    verified = False
    email = request.form['loginuseremail']
    password = request.form['loginuserpassword']
    try:
        v = validate_email(email)
        validated_email = v.email
        print(validated_email)
    except EmailNotValidError as e:
        print('Invalid Email address',e)
        InvalidEmail = True
        return render_template('index.html',InvalidEmail= InvalidEmail)
    else:

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE Email = %s AND Password = %s", (email, password))
        data = cur.fetchone()
        cur.close()

        # print(data)
        if data:
            verified = True
            return render_template("home.html", verified = verified)
        else:       
            return render_template("index.html", verified = verified)



@app.route('/add_video', methods=['GET','POST'])
def add_video():
    global video_url
    global video_id
    video_url = request.form['videoUrl']
    video_id = get_youtube_id(video_url)
    # video_title = get_video_title(video_url)

    if video_id:
        print(video_id)
        vurl = "https://www.youtube.com/embed/" + video_id
        save_path = "./video_audio_files"

        if file_exists_in_folder("./video_audio_files", video_id+".mp4"):
            return render_template('video_page.html', video_url = vurl)
              
        threading.Thread(target=download_video, args=(video_url, save_path, video_id)).start()
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


@app.route('/back', methods=['GET', 'POST'])
def back():
    global output_text
    global video_url
    global time
    global subtopic
    global video_id
    global onComplete
    global transcript
    global subtitles

    output_text = None
    video_url = None
    time = 0
    subtopic = None
    video_id = None
    onComplete = 0
    transcript = None
    subtitles = None

    return render_template("home.html")

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
    global time
    global subtopic
    global subtitles

    # time = 0
      
    if file_exists_in_folder("./video_audio_files", video_id+".srt"):
        return render_template("subtopic_skip.html", time=time, video_id=video_id)

    # Building srt file
    if transcript is None:
        transcript = get_transcript(video_id)
        
    subtitles = transcript.export_subtitles_srt()
    f = open("./video_audio_files/"+video_id+".srt", "a")
    f.write(subtitles)
    f.close()

    # print(subtitles)
    # print(type(subtitles))
    # print('-----------------------------------------')
    return render_template("subtopic_skip.html", time=time, video_id = video_id)
    

@app.route('/video_skip', methods=['POST','GET'])
def video_skip():
    global time
    global subtopic
    global video_id
    global subtitles
    
    data = request.json
    # time = 0
    if subtitles is None:
        subtitles = parse_srt("./video_audio_files/"+video_id+".srt")
    
    # print(subtitles)
    # print(type(subtitles))

    subtopic = data['topic']
    timestamp = find_subtitle_containing_text(subtitles, subtopic)
    # print(timestamp)
    # print(type(timestamp))
    
    if timestamp is not None:
        time = parse_time(timestamp)
    else:
        print('Subtopic not found in subtitles')

    return jsonify({'time': time})


@app.route('/next_timestamp', methods=['POST', 'GET'])
def next_timestamp():
    global subtitles
    global time
    global subtopic
    current_timestamp = time
    
    # Split the subtitles into blocks
    subtitle_blocks = subtitles.strip().split('\n\n')
    
    for block in subtitle_blocks:
        lines = block.split('\n')
        
        # Extract start time from the second line
        start_time_line = lines[1]
        start_time_str = start_time_line.split(' --> ')[0]
        start_time = start_time_str.strip()
        
        # Extract text from the remaining lines
        text = ' '.join(lines[2:])
        start_time = parse_time(start_time)
        # Check if subtopic is in the text and start time is greater than current time
        if subtopic.lower() in text.lower() and start_time > current_timestamp:
            time = start_time
            # print(time)
            return jsonify({'next_time': time})
            # return start_time
    
    print('No next timestamp found for the given subtopic.')
    return None

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
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()    
    return content


def parse_time(time_str):
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2].replace(',', '.'))
    return hours * 3600 + minutes * 60 + seconds


def find_subtitle_containing_text(subtitles, subtopic):
    subtitle_blocks = subtitles.strip().split('\n\n')  # Split into subtitle blocks
    
    for block in subtitle_blocks:
        lines = block.split('\n')  # Split block into lines
        
        # Extract start time from the second line
        start_time_line = lines[1]
        start_time_str = start_time_line.split(' --> ')[0]
        start_time = start_time_str.strip()
        
        # Extract text from the remaining lines
        text = ' '.join(lines[2:])
        
        # Check if subtopic is in the text
        if subtopic.lower() in text.lower():
            return start_time
    
    return None


def file_exists_in_folder(folder_path, filename):
    # Get list of files in the folder
    files = os.listdir(folder_path)
    # Check if the filename exists in the list of files
    return filename in files



# Main method

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
