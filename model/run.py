import cv2
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box
from collections import deque
import time
import openpyxl
from openpyxl import Workbook
from datetime import datetime

def box_iou(box1, box2):
    poly1 = shapely_box(box1[0], box1[1], box1[2], box1[3])
    poly2 = shapely_box(box2[0], box2[1], box2[2], box2[3])
    iou = poly1.intersection(poly2).area / poly1.union(poly2).area
    return iou

class VehicleTracker:
    def __init__(self, max_age=30):
        self.vehicles = {}
        self.max_age = max_age
    #Updates the tracker with new vehicle detections
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
        #Removing Old Vehicles
        for track_id in list(self.vehicles.keys()):
            if track_id not in current_ids:
                self.vehicles[track_id]['last_seen'] += 1
                if self.vehicles[track_id]['last_seen'] > self.max_age:
                    del self.vehicles[track_id]
    #Get Vehicle Speed Method
    def get_vehicle_speed(self, track_id, pixels_per_meter):
        if track_id in self.vehicles and len(self.vehicles[track_id]['positions']) > 1:
            start = self.vehicles[track_id]['positions'][0]
            end = self.vehicles[track_id]['positions'][-1]
            # Calculate distance in pixels
            distance_in_pixels = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            # Convert distance to meters
            distance_in_meters = distance_in_pixels / pixels_per_meter
            # Calculate time in seconds (assuming 30 fps)
            time_in_seconds = len(self.vehicles[track_id]['positions']) / 30
            # Calculate speed in m/s and convert to km/h
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
        heavy_vehicle_count = sum(1 for v in self.vehicle_tracker.vehicles.values() if v['type'] in [5, 7, 80])  # 5 - Bus, 7 - Truck, 80 - JCB
        
        # Calculate average speed of all vehicles
        speeds = [self.vehicle_tracker.get_vehicle_speed(id, 100) for id in self.vehicle_tracker.vehicles]
        avg_speed = np.mean(speeds) if speeds else 0  # Handle empty speeds list

        is_traffic_jam = avg_speed < 5 and vehicle_count > 10  # If average speed < 5 km/h and more than 10 vehicles then jam
        # too_many_heavy_vehicles = heavy_vehicle_count / vehicle_count > self.heavy_vehicle_threshold if vehicle_count > 0 else False
        too_many_heavy_vehicles = heavy_vehicle_count > 30  # If more than 6 heavy vehicles
        
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
            return (vehicle_count * 5) / avg_speed  # Assuming 5 meters per vehicle
        return float('inf')

    def decide_traffic_light(self, is_traffic_jam, too_many_heavy_vehicles, avg_speed):
        if is_traffic_jam:
            return 'green', 120  # 2 minutes
        elif too_many_heavy_vehicles:
            return 'green', 90  # 1.5 minutes
        elif avg_speed < 10:
            return 'green', 60  # 1 minute
        else:
            return 'red', 30  # 30 seconds
        
# Function to display text with a white background
def display_text_with_background(frame, text, pos, font_scale=0.7, font_thickness=2, text_color=(0, 0, 0), bg_color=(255, 255, 255)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
    
    # Draw the white rectangle as background
    cv2.rectangle(frame, (pos[0], pos[1] - text_height - baseline), (pos[0] + text_width, pos[1] + baseline), bg_color, cv2.FILLED)
    
    # Put the text on top of the white rectangle
    cv2.putText(frame, text, pos, font, font_scale, text_color, font_thickness)

def initialize_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Vehicle Data"
    headers = ['Timestamp', 'x1', 'y1', 'x2', 'y2', 'Width', 'Height', 'Class Label', 'Confidence', 'Track ID']
    ws.append(headers)
    return wb, ws

def log_to_excel(ws, timestamp, x1, y1, x2, y2, class_name, confidence, track_id):
    width = x2 - x1
    height = y2 - y1
    row = [timestamp, x1, y1, x2, y2, width, height, class_name, confidence, track_id]
    ws.append(row)

def main():
    model1 = YOLO('yolo11l.pt')
    model2 = YOLO('best.pt')
    
    video_source = "C:\\Users\\Vedan\\OneDrive\\Desktop\\YOLO Vehicle Counter\\YOLOv8-DeepSORT-Object-Tracking\\Indian Traffic Dataset - Made with Clipchamp.mp4"
    cap = cv2.VideoCapture(video_source)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))
    
    model1_bias = 0.7 #YOLO11l
    model2_bias = 0.71 #Custom Model
    
    frame_skip = 4
    frame_count = 0
    
    road_area = width * height # Area of road assumption
    traffic_analyzer = TrafficAnalyzer(road_area)
    
    # Initialize Excel workbook and worksheet
    wb, ws = initialize_excel()
    logged_tracks = set()

    # Open the Excel file for writing
    excel_file = 'detections.xlsx'
    wb.save(excel_file)

    try:
        while True:
            ret, frame = cap.read()
            frame_count += 1
            if not ret or frame_count % frame_skip != 0:
                continue
            
            results1 = model1.track(frame, classes=[1, 2, 3, 5, 7], conf=0.05, iou=0.9, persist=True)  # BotSort
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
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for box in filtered_boxes:
                x1, y1, x2, y2, confidence, class_id, track_id, model_index = box
                model = model1 if model_index == 0 else model2
                class_name = model.names[class_id]
                color = (0, 255, 0) if model_index == 0 else (0, 255, 0)
                confidence /= model1_bias if model_index == 0 else model2_bias
                label = f"{class_name} {confidence:.2f} ID:{track_id}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                
                # Log to Excel if it's a new track_id
                if track_id != -1 and track_id not in logged_tracks:
                    log_to_excel(ws, timestamp, x1, y1, x2, y2, class_name, confidence, track_id)
                    logged_tracks.add(track_id)
            
            # Display traffic analysis results
            display_text_with_background(frame, f"Vehicle Count: {traffic_analysis['vehicle_count']}", (10, 30))
            display_text_with_background(frame, f"Avg Speed: {traffic_analysis['avg_speed']:.2f} km/h", (10, 60))
            display_text_with_background(frame, f"Traffic Jam Condition: {'Yes' if traffic_analysis['is_traffic_jam'] else 'No'}", (10, 90))
            display_text_with_background(frame, f"Many Heavy Vehicles Present: {'Yes' if traffic_analysis['too_many_heavy_vehicles'] else 'No'}", (10, 120))
            display_text_with_background(frame, f"Est. Road Clearance Time: {traffic_analysis['estimated_clearance_time']:.2f}s", (10, 150))
            display_text_with_background(frame, f"Suggested Traffic Light: {traffic_analysis['traffic_light_decision'][0]} for {traffic_analysis['traffic_light_decision'][1]}s", (10, 180))
            
            # out.write(frame)
            cv2.imshow('Adaptive Traffic Control', frame)
            
            # Save the Excel file after each frame
            wb.save(excel_file)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Make sure to save the Excel file one last time before closing
        wb.save(excel_file)
        
        cap.release()
        # out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()