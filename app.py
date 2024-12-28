from flask import Flask, render_template, Response, jsonify, request, flash
from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
from flask_ngrok import run_with_ngrok
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import cv2
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box
from collections import deque
import time
import yt_dlp
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
import gspread
import gnupg
import getpass
import signal
import atexit
from dotenv import load_dotenv

load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# run_with_ngrok(app)

# Initialize GPG instance
gpg = gnupg.GPG()

# Prompt user for passphrase
passphrase = getpass.getpass("Enter passphrase for decryption: ")

# Path to the encrypted file
input_file = "credentials.json.gpg"
output_file = "credentials.json"

# Cleanup function to delete the decrypted file
def cleanup():
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Deleted decrypted file: {output_file}")

# Register cleanup function to run at program exit
atexit.register(cleanup)

# Handle signals like Ctrl+C (SIGINT) or termination (SIGTERM)
def handle_exit_signals(signum, frame):
    print(f"Received termination signal ({signum}). Cleaning up...")
    cleanup()
    exit(0)

# Attach signal handlers
signal.signal(signal.SIGINT, handle_exit_signals)  # For Ctrl+C
signal.signal(signal.SIGTERM, handle_exit_signals)  # For termination signals

# Decrypt the file symmetrically

with open(input_file, "rb") as f:
    status = gpg.decrypt_file(
        f,
        output=output_file,
        passphrase=passphrase
    )

# Check the result
if status.ok:
    print(f"File successfully decrypted: {output_file}")
    # Add logic here to use the decrypted file, e.g., load credentials
else:
    print(f"Decryption failed: {status.status}")


# Global variables
global_sheet = None
traffic_analysis_data = {}  # Initialize the global variable

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Define the scopes required for the Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/spreadsheets']

# Use service account credentials to authenticate
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Sheets configurations
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

import gspread

# Define the LoginForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Function to initialize the Google Sheet connection
def initialize_google_sheets(sheet_name):
    """Initializes and returns the Google Sheets client and sheet."""
    # Open the Google Sheet without authorization
    client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sheet = client.open(sheet_name).sheet1  # Assumes you want the first sheet
    return sheet

# Function to log data to Google Sheets
def log_to_google_sheets(timestamp, x1, y1, x2, y2, class_name, confidence, track_id):
    global global_sheet  # Declare the global variable
    if global_sheet is None:
        global_sheet = initialize_google_sheets('vehicle-detection')  # Replace 'Sheet1' with your actual sheet name
    
    # Add headers if the sheet is empty
    if not global_sheet.row_values(1):
        headers = ['Timestamp', 'X1', 'Y1', 'X2', 'Y2', 'Width', 'Height', 'Class Name', 'Confidence', 'Track ID']
        global_sheet.insert_row(headers, 1)

    # Calculate width and height
    width = x2 - x1
    height = y2 - y1

    # Prepare and append row data
    row = [timestamp, x1, y1, x2, y2, width, height, class_name, confidence, track_id]
    global_sheet.append_row(row)

def fetch_data_from_sheets():
    global global_sheet
    if global_sheet is None:
        global_sheet = initialize_google_sheets('vehicle-detection')  # Replace with your sheet name
    
    # Fetch all data, excluding the header row
    rows = global_sheet.get_all_records(head=1)  # Skips the header row by default
    print(rows)  # Log rows fetched from Google Sheets

def box_iou(box1, box2):
    poly1 = shapely_box(box1[0], box1[1], box1[2], box1[3])
    poly2 = shapely_box(box2[0], box2[1], box2[2], box2[3])
    iou = poly1.intersection(poly2).area / poly1.union(poly2).area
    return iou

class VehicleTracker:
    def __init__(self, max_age=30):
        self.vehicles = {}
        self.max_age = max_age

    def update(self, detections):
        current_ids = set()
        for detection in detections:
            track_id = detection[6]
            if track_id != -1:
                current_ids.add(track_id)
                if track_id not in self.vehicles:
                    self.vehicles[track_id] = {'positions': deque(maxlen=30), 'last_seen': 0, 'type': detection[5]}
                self.vehicles[track_id]['positions'].append(detection[:4])
                self.vehicles[track_id]['last_seen'] = 0
        for track_id in list(self.vehicles.keys()):
            if track_id not in current_ids:
                self.vehicles[track_id]['last_seen'] += 1
                if self.vehicles[track_id]['last_seen'] > self.max_age:
                    del self.vehicles[track_id]

    def get_vehicle_speed(self, track_id, pixels_per_meter):
        if track_id in self.vehicles and len(self.vehicles[track_id]['positions']) > 1:
            start = self.vehicles[track_id]['positions'][0]
            end = self.vehicles[track_id]['positions'][-1]
            distance_in_pixels = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            distance_in_meters = distance_in_pixels / pixels_per_meter
            time_in_seconds = len(self.vehicles[track_id]['positions']) / 30
            speed_meters_per_second = distance_in_meters / time_in_seconds if time_in_seconds > 0 else 0
            speed_kmh = speed_meters_per_second * 3.6
            return speed_kmh
        return 0


class TrafficAnalyzer:
    def __init__(self, road_area, heavy_vehicle_threshold=0.3):
        self.road_area = road_area
        self.heavy_vehicle_threshold = heavy_vehicle_threshold
        self.vehicle_tracker = VehicleTracker()

    def analyze_traffic(self, detections):
        self.vehicle_tracker.update(detections)
        
        vehicle_count = len(self.vehicle_tracker.vehicles)
        heavy_vehicle_count = sum(1 for v in self.vehicle_tracker.vehicles.values() if v['type'] in [5, 7, 80])
        
        speeds = [self.vehicle_tracker.get_vehicle_speed(id, 100) for id in self.vehicle_tracker.vehicles]
        avg_speed = np.mean(speeds) if speeds else 0

        is_traffic_jam = avg_speed < 5 and vehicle_count > 10
        too_many_heavy_vehicles = heavy_vehicle_count > 30
        
        estimated_clearance_time = self.estimate_clearance_time(vehicle_count, avg_speed)
        
        traffic_light_decision = self.decide_traffic_light(is_traffic_jam, too_many_heavy_vehicles, avg_speed)
        
        return {
            'vehicle_count': vehicle_count,
            'avg_speed': avg_speed,
            'is_traffic_jam': is_traffic_jam,
            'too_many_heavy_vehicles': too_many_heavy_vehicles,
            'estimated_clearance_time': estimated_clearance_time,
            'traffic_light_decision': traffic_light_decision
        }

    def estimate_clearance_time(self, vehicle_count, avg_speed):
        if avg_speed > 0:
            return (vehicle_count * 5) / avg_speed
        return float('inf')

    def decide_traffic_light(self, is_traffic_jam, too_many_heavy_vehicles, avg_speed):
        if is_traffic_jam:
            return 'green', 120
        elif too_many_heavy_vehicles:
            return 'green', 90
        elif avg_speed < 10:
            return 'green', 60
        else:
            return 'red', 30


def get_youtube_stream_url(video_url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_url = info['url']
        return video_url

def initialize_youtube_stream(video_id):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    stream_url = get_youtube_stream_url(video_url)
    return stream_url


# Global variable to control video visibility
show_video = True

def generate_frames():
    global traffic_analysis_data, global_sheet, show_video

    model1 = YOLO('yolo11l.pt')
    model2 = YOLO('best.pt')

    cap = cv2.VideoCapture(initialize_youtube_stream(global_video_id))
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    model1_bias = 0.7
    model2_bias = 0.71
    
    frame_skip = 4
    frame_count = 0
    
    road_area = width * height
    traffic_analyzer = TrafficAnalyzer(road_area)
    
    logged_tracks = set()

    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        if not ret or frame_count % frame_skip != 0:
            continue
        
        results1 = model1.track(frame, classes=[1, 2, 3, 5, 7], conf=0.05, iou=0.9, persist=True)
        results2 = model2.track(frame, classes=[80, 81, 82, 83, 84], iou=0.9, persist=True)
        
        combined_boxes = []
        for i, results in enumerate([results1, results2]):
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(float, box.xyxy[0])
                    confidence = float(box.conf[0])
                    confidence *= model1_bias if i == 0 else model2_bias
                    class_id = int(box.cls[0])
                    track_id = int(box.id[0]) if box.id is not None else -1
                    combined_boxes.append((x1, y1, x2, y2, confidence, class_id, track_id, i))
        
        combined_boxes.sort(key=lambda x: x[4], reverse=True)
        
        filtered_boxes = []
        for box in combined_boxes:
            if not any(box_iou(box[:4], kept_box[:4]) > 0.6 for kept_box in filtered_boxes):
                filtered_boxes.append(box)
        
        traffic_analysis = traffic_analyzer.analyze_traffic(filtered_boxes)
        traffic_analysis_data = traffic_analysis

        # Create a blank frame if show_video is False
        if not show_video:
            frame = np.zeros((height, width, 3), dtype=np.uint8)  # Black background
        
        timestamp = datetime.now().strftime("%H:%M:%S %d,%m,%Y")
        
        for box in filtered_boxes:
            x1, y1, x2, y2, confidence, class_id, track_id, model_index = box
            model = model1 if model_index == 0 else model2
            class_name = model.names[class_id]
            color = (0, 255, 0) if model_index == 0 else (0, 255, 0)
            confidence /= model1_bias if model_index == 0 else model2_bias
            label = f"{class_name} {confidence:.2f} ID:{track_id}"
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            if track_id != -1 and track_id not in logged_tracks:
                log_to_google_sheets(timestamp, x1, y1, x2, y2, class_name, confidence, track_id)
                logged_tracks.add(track_id)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/toggle_video', methods=['POST'])
def toggle_video():
    global show_video
    show_video = not show_video
    return jsonify({"show_video": show_video, "message": "Video visibility toggled."})


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Route for the login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        # print(username)
        password = form.password.data
        # print(password)
        # Dummy authentication (replace with real authentication logic)
        if username == "test" and password == "test123":
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            form.username.data = ''
            form.password.data = ''
    return render_template('login.html', form=form)

# Route for the home page
@app.route('/enterrurl')
def home():
    session.clear()
    return render_template('youtube.html')

# @app.route('/')
# def index():
#     return render_template('youtube.html')


def extract_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1]
    return None


global_video_id = None
cache = {
    'data': None,
    'timestamp': 0
}
CACHE_DURATION = 30  # Cache duration in seconds

@app.route('/submit', methods=['POST'])
def submit():
    youtube_url = request.form['youtube_url']
    
    global global_video_id
    video_id = extract_video_id(youtube_url)
    global_video_id = video_id
    
    return redirect(url_for('dashboard'))

@app.route('/index')
def dashboard():
    try:
        global global_sheet
        if global_sheet is None:
            global_sheet = initialize_google_sheets('vehicle-detection')  # Replace with your sheet name

        # Fetch all data, excluding the header row
        rows = get_cached_data()

        if not rows:
            rows = []  # Ensure rows is always a list to avoid template issues

        return render_template('dashboard.html', data=rows)
    except Exception as e:
        app.logger.error(f"Error in dashboard route: {e}")
        return render_template('error.html', message="Unable to fetch data. Please try again later."), 500

@app.route('/get_chart_data')
def get_chart_data():
    rows = get_cached_data()

    # Process the data
    classLabels = {}
    timeData = {}
    roadOccupancy = {}
    for row in rows:
        timestamp = row['Timestamp']
        classLabel = row['Class Name']
        width = float(row['Width'])
        height = float(row['Height'])
        area = width * height

        # Count occurrences for Class Label
        classLabels[classLabel] = classLabels.get(classLabel, 0) + 1

        # Count vehicles per minute
        timeKey = timestamp.split()[0][:5]  # Get HH:MM from the timestamp
        timeData[timeKey] = timeData.get(timeKey, 0) + 1

        # Road Occupancy
        roadOccupancy[classLabel] = roadOccupancy.get(classLabel, 0) + area

    return jsonify({
        'classLabels': {'keys': list(classLabels.keys()), 'values': list(classLabels.values())},
        'timeData': {'keys': list(timeData.keys()), 'values': list(timeData.values())},
        'roadOccupancy': {'keys': list(roadOccupancy.keys()), 'values': list(roadOccupancy.values())}
    })

def get_cached_data():
    global cache, global_sheet
    current_time = time.time()
    if cache['data'] is None or current_time - cache['timestamp'] > CACHE_DURATION:
        if global_sheet is None:
            global_sheet = initialize_google_sheets('vehicle-detection')
        cache['data'] = global_sheet.get_all_records(head=1)
        cache['timestamp'] = current_time
    return cache['data']

@app.route('/traffic_data')
def traffic_data():
    analysis_data_serializable = {
        'vehicle_count': int(traffic_analysis_data.get('vehicle_count', 0)),
        'avg_speed': float(traffic_analysis_data.get('avg_speed', 0.0)),
        'is_traffic_jam': bool(traffic_analysis_data.get('is_traffic_jam', False)),
        'too_many_heavy_vehicles': bool(traffic_analysis_data.get('too_many_heavy_vehicles', False)),
        'estimated_clearance_time': float(traffic_analysis_data.get('estimated_clearance_time', 0.0)),
        'traffic_light_decision': traffic_analysis_data.get('traffic_light_decision', ["Red", 30])
    }

    return jsonify(analysis_data_serializable)


if __name__ == '__main__':
    app.run()