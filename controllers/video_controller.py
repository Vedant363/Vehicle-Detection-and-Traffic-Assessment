from flask import render_template, Blueprint, Response, jsonify
from models.tracking import generate_frames

video_bp = Blueprint('video', __name__)

@video_bp.route('/toggle_video', methods=['POST'])
def toggle_video():
    try:
        print("toggle_video -------------------------------")
        from models.state import VideoState
        VideoState.set_show_video(not VideoState.get_show_video())
        return jsonify({"show_video": VideoState.get_show_video(), "message": "Video visibility toggled."})
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /toggle_video"), 500

@video_bp.route('/video_feed')
def video_feed():
    try:
        print("Video feed -------------------------------")
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /video_feed"), 500