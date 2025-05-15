import cv2
import numpy as np
import torch
from ultralytics import YOLO
import signal

# For analyzing traffic
traffic_analysis_data = {}

def get_show_video():
    from models.state import VideoState  
    return VideoState.get_show_video()

def stop_execution():
    from models.state import StopExecution  
    return StopExecution.get_stop_execution_status()

def complete_stop():
    from models.state import StopExecution
    StopExecution.set_stop_execution_status(True)
    signal.raise_signal(signal.SIGINT)

def box_iou(box1, box2):
    from shapely.geometry import box as shapely_box
    poly1 = shapely_box(box1[0], box1[1], box1[2], box1[3])
    poly2 = shapely_box(box2[0], box2[1], box2[2], box2[3])
    iou = poly1.intersection(poly2).area / poly1.union(poly2).area
    return iou

class VehicleTracker:
    def __init__(self, max_age=30):
        self.vehicles = {}
        self.max_age = max_age

    def update(self, detections):
        from collections import deque
        import numpy as np

        current_ids = set()
        for detection in detections:
            track_id = detection[6]
            if track_id != -1:
                current_ids.add(track_id)
                if track_id not in self.vehicles:
                    self.vehicles[track_id] = {
                        'positions': deque(maxlen=30),
                        'last_seen': 0,
                        'type': detection[5]
                    }
                self.vehicles[track_id]['positions'].append(detection[:4])
                self.vehicles[track_id]['last_seen'] = 0
        for track_id in list(self.vehicles.keys()):
            if track_id not in current_ids:
                self.vehicles[track_id]['last_seen'] += 1
                if self.vehicles[track_id]['last_seen'] > self.max_age:
                    del self.vehicles[track_id]

    def get_vehicle_speed(self, track_id, pixels_per_meter):
        import numpy as np
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
        import numpy as np

        self.vehicle_tracker.update(detections)
        vehicle_count = len(self.vehicle_tracker.vehicles)
        heavy_vehicle_count = sum(1 for v in self.vehicle_tracker.vehicles.values() 
                                  if v['type'] in [5, 7, 80])

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

def log_to_google_sheets(timestamp, x1, y1, x2, y2, class_name, confidence, track_id):
    from models.sheets import global_sheet, initialize_google_sheets

    global stored_rows, header_inserted
    if 'stored_rows' not in globals():
        stored_rows = []

    if 'header_inserted' not in globals():
        header_inserted = False  

    if global_sheet is None:
        global_sheet = initialize_google_sheets('vehicle-detection')

    # Insert the header only once
    if not header_inserted:
        try:
            if not global_sheet.row_values(1):  
                headers = ['Timestamp', 'X1', 'Y1', 'X2', 'Y2', 'Width', 'Height', 'Class Name', 'Confidence', 'Track ID']
                global_sheet.insert_row(headers, 1)
            header_inserted = True
        except Exception as e:
            print(f"Error checking/inserting header: {e}")

    width = x2 - x1
    height = y2 - y1

    row = [timestamp, x1, y1, x2, y2, width, height, class_name, confidence, track_id]
    stored_rows.append(row)

    if len(stored_rows) >= 25:
        try:
            global_sheet.append_rows(stored_rows)
            stored_rows.clear()  
        except Exception as e:
            print(f"Error appending rows: {e}")

logged_tracks = set()

def generate_frames():
    global traffic_analysis_data, logged_tracks

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    model1 = YOLO('yolo11n.pt')
    model2 = YOLO('best.pt') # Custom YOLO11n model, can be replaced with best_l.pt

    # --- For IP Camera based Traffic Detection ---
    # from models.ip_camera_stream import initialize_ip_camera_stream
    # from controllers.main_controller import global_stream_url
    # cap = initialize_ip_camera_stream(global_stream_url)

    # --- For Youtube Stream based Traffic Detection ---
    from models.youtube_stream import initialize_youtube_stream
    from controllers.main_controller import global_video_id
    cap = cv2.VideoCapture(initialize_youtube_stream(global_video_id))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # If FPS is 0 or not found, default to 30
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    model1_bias = 0.7
    model2_bias = 0.71
    frame_skip = 5
    frame_count = 0
    road_area = width * height
    traffic_analyzer = TrafficAnalyzer(road_area)

    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        if not ret or frame_count % frame_skip != 0:
            continue

        if stop_execution():
            break

        results1 = model1.track(frame, classes=[1, 2, 3, 5, 7], conf=0.05, iou=0.9, persist=True, device=device)
        results2 = model2.track(frame, classes=[80, 81, 82, 83, 84], iou=0.9, persist=True, device=device)

        combined_boxes = []
        for i, results in enumerate([results1, results2]):
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(float, box.xyxy[0])
                    confidence = float(box.conf[0])
                    confidence *= (model1_bias if i == 0 else model2_bias)
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

        # If show_video is off, replace frame with blank
        if not get_show_video():
            frame = np.zeros((height, width, 3), dtype=np.uint8)

        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S %d,%m,%Y")

        for box in filtered_boxes:
            x1, y1, x2, y2, confidence, class_id, track_id, model_index = box
            model = model1 if model_index == 0 else model2
            class_name = model.names[class_id]
            color = (0, 255, 0)
            # Restore confidence
            confidence /= (model1_bias if model_index == 0 else model2_bias)
            label = f"{class_name} {confidence:.2f} ID:{track_id}"
            cv2.putText(frame, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            if track_id != -1 and track_id not in logged_tracks:
                log_to_google_sheets(timestamp, x1, y1, x2, y2, class_name, confidence, track_id)
                logged_tracks.add(track_id)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )

    cap.release()