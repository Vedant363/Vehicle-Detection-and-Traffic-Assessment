import cv2

def initialize_ip_camera_stream(ip_stream_url: str):
    if not ip_stream_url:
        raise ValueError("IP stream URL is empty.")

    cap = cv2.VideoCapture(ip_stream_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        raise ValueError(f"Failed to open IP stream: {ip_stream_url}")

    return cap