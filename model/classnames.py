import cv2
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box
from collections import deque

# Load the model
model = YOLO('best.pt')

# Get the names of the classes
# Iterate over all classes
for class_index in range(len(model.names)):
    class_name = model.names[class_index]
    print(f"Class ID: {class_index}, Class Name: {class_name}")
