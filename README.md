# **Vehicle Detection and Traffic Assessment using YOLO11L**

This project is a **real-time vehicle detection and traffic assessment system** built on a self-trained **YOLO11L model**. The system integrates advanced features like **data logging**, **visualization**, and **traffic analysis** to provide actionable insights into traffic conditions.

![License](https://img.shields.io/github/license/Vedant363/Vehicle-Detection-and-Traffic-Assessment?color=gold)
![Last Commit](https://img.shields.io/github/last-commit/Vedant363/Vehicle-Detection-and-Traffic-Assessment?color=orange)
![Build Status](https://img.shields.io/badge/build-passing-neongreen)
![Visitors](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/Vedant363/Vehicle-Detection-and-Traffic-Assessment&count_bg=red)




## 🖼️ **Preview**
![Photo 1](static/photo1.png)



## ✨ **Features**

### 🚘 **Vehicle Detection**
- Detects multiple vehicle types in real-time using a **combination of the base YOLO11L model** (for pre-trained classes) and **custom-trained YOLO11L model** (for added custom classes).
- Base YOLO11L model from [Ultralytics](https://docs.ultralytics.com/models/yolo11/).

| **Model**    | **Size (pixels)** | **mAPval 50-95** | **Speed (CPU ONNX)** | **Speed (T4 TensorRT10)** | **Params (M)** | **FLOPs (B)** |
|--------------|-------------------|------------------|-----------------------|---------------------------|----------------|---------------|
| YOLOv11L     | 640               | 53.4             | 238.6 ± 1.4 ms        | 6.2 ± 0.1 ms              | 25.3           | 86.9          |

- **Custom-trained YOLO11L model** supports **80 COCO classes** and **5 additional custom classes** for vehicle detection:
  - **80: JCB**
  - **81: Auto**
  - **82: Rickshaw**
  - **83: Cart**
  - **84: Scooter**
  
- Results of training for the **Custom-trained YOLO11L model**:
  
  ![Results](model/results.png)
  
- **Achieved Performance Metrics on Testing Data:**
  - **mAP50-95:** 59.5%
  - **mAP50:** 66.2%
  - **mAP75:** 61.3%

- **Class-Wise Performance Metrics on Testing Data:**

| **Class**     | **Precision** | **Recall** | **mAP50** | **mAP50-95** |
|---------------|---------------|------------|-----------|--------------|
| JCB           | 0.907         | 0.754      | 0.878     | 0.771        |
| Auto          | 0.913         | 0.766      | 0.909     | 0.807        |
| Rickshaw      | 0.862         | 0.728      | 0.868     | 0.811        |
| Cart          | 0.852         | 0.603      | 0.781     | 0.627        |
| Scooter       | 0.908         | 0.809      | 0.936     | 0.875        |




### 📋 **Data Logging**
- Logs detection data to **Google Sheets** for further analysis.
- Captures the following parameters:
  - **Timestamp**
  - **Bounding Box Coordinates** (X1, Y1, X2, Y2)
  - **Width and Height** of detected vehicles
  - **Class Name**
  - **Confidence Score**
  - **Track ID**



### 📊 **Data Visualization**
Provides real-time visual insights using **Chart.js**:
1. **Pie Chart**: Proportion of detected vehicle classes.
2. **Line Chart**: Number of vehicles detected over time.
3. **Bar Chart**: Vehicle classes with the most road occupancy, calculated by bounding box area.



### 🚦 **Traffic Insights**
Real-time calculations based on detection data:
- **Vehicle Count**: Total number of vehicles detected in the current frame.
- **Average Speed**: Estimates the speed of moving vehicles.
- **Traffic Jam Detection**: Identifies congestion based on density.
- **Heavy Vehicle Density**: Analyzes the proportion of heavy vehicles present.
- **Road Clearance Time**: Predicts the time required to clear the road.
- **Traffic Light Suggestions**: Recommends optimal traffic light timings based on vehicle density and flow.



## 🔄 **Workflow**

1. **Input Video Stream**:
   - The system uses YouTube streams as the input source.
   - Frames are extracted using OpenCV for processing.

2. **Detection and Analysis**:
   - The YOLO11L model detects vehicles and classifies them into predefined classes.
   - Detection results include bounding box dimensions, class names, confidence scores, and unique track IDs.

3. **Data Logging to Google Sheets**:
   - Detected data is dynamically updated in Google Sheets.
   - Utilizes Google Sheets API for seamless integration and real-time updates.

4. **Visualization**:
   - Chart.js fetches data from Google Sheets to render interactive charts.
   - Provides intuitive insights through pie, line, and bar charts.

5. **Traffic Insights Calculation**:
   - Algorithms calculate traffic-related metrics and predictions.
   - Displays results on the web interface for user interpretation.



## 🛠️ **Technical Overview**

### Backend
- **Flask Framework**: Handles application logic and APIs.
- **Flask-WTF**: Validates user inputs and forms.
- **Flask-Ngrok**: Facilitates local hosting for development purposes.
- **YOLO11L Model**: Custom-trained model for vehicle detection and classification.

### Frontend
- **Chart.js**: Enables dynamic data visualization.
- **HTML & CSS**: Renders the web interface.

### Libraries and Tools
- **OpenCV**: Processes video frames for detection.
- **Shapely**: Calculates geometric properties for bounding boxes.
- **yt_dlp**: Streams YouTube videos for input.
- **GSpread**: Integrates with Google Sheets for data logging.
- **Google Sheets API**: Facilitates real-time updates and data storage.



## 📤 **Example Outputs**

### **Detection Data Logged**
| **Timestamp**          | **X1**        | **Y1**       | **X2**        | **Y2**       | **Width**     | **Height**    | **Class Name** | **Confidence** | **Track ID** |
|------------------------|---------------|--------------|---------------|--------------|---------------|---------------|----------------|----------------|--------------|
| 21:49:05 1/1/2025      | 32.65145874   | 214.776062   | 124.6397705   | 275.8533325  | 91.98831177   | 61.07727051   | car            | 0.9123997688   | 1            |
| 21:49:05 1/1/2025      | 388.3595581   | 102.7689667  | 420.4992065   | 138.6712799  | 32.13964844   | 35.90231323   | scooter        | 0.8495836258   | 2            |
| 21:49:05 1/1/2025      | 62.71186829   | 150.5038757  | 96.41931152   | 185.9692078  | 33.70744324   | 35.46533203   | auto           | 0.8151150942   | 3            |
| 21:49:05 1/1/2025      | 157.4563141   | 140.8128662  | 195.0846405   | 168.6981506  | 37.62832642   | 27.88528442   | car            | 0.7732740045   | 4            |
| 21:49:05 1/1/2025      | 287.2844238   | 136.8283691  | 320.9523926   | 169.0031128  | 33.66796875   | 32.17474365   | car            | 0.7720789313   | 5            |

### **Visualization Charts**
- **Bar Chart**: Highlights vehicle classes with the most road occupancy based on their dimensions.
  
![Bar Chart](static/bar.png)


## 🚀 **Future Enhancements**

- **Integration with Traffic Management Systems**: Expand the system for live traffic control with live traffic stream from CCTVs and sensors.
- **Custom Class Expansion**: Train the model with additional vehicle classes for broader detection.



## 📝 **License**
This project is licensed under the **CC0 1.0 Universal**. See the [LICENSE](LICENSE.md) file for details.
