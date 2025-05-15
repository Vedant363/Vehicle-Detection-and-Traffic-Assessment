import cv2
import sys 

def initialize_ip_camera_stream(ip_camera_url: str):
    
    print(f"Attempting to open IP camera stream: {ip_camera_url}")

    cap = cv2.VideoCapture(ip_camera_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print(f"Error: Could not open IP camera stream from {ip_camera_url}")
        print("Please check the URL, network connection, and camera status.")
        sys.exit("Failed to open IP camera stream.")

    print("IP camera stream opened successfully.")
    return cap

# --- Testing the ip camera stream --- 
# if __name__ == '__main__':
#     
#     test_url = 'rtsp://your_test_ip_camera_address/stream_path'
#     camera_capture = initialize_ip_camera_stream(test_url)
#
#     if camera_capture:
#         print("Camera capture object created.")
#     
#         ret, frame = camera_capture.read()
#         if ret:
#             print(f"Successfully read a frame: {frame.shape}")
#         else:
#             print("Failed to read a frame.")
#
#         camera_capture.release()
#         print("Camera capture object released.")