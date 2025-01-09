from flask import render_template, Blueprint, Response, jsonify
from models.tracking import generate_frames
from controllers.main_controller import login_required, url_required

video_bp = Blueprint('video', __name__)

@video_bp.route('/toggle_video', methods=['POST'])
@login_required
@url_required
def toggle_video():
    try:
        from models.state import VideoState
        VideoState.set_show_video(not VideoState.get_show_video())
        return jsonify({"show_video": VideoState.get_show_video(), "message": "Video visibility toggled."})
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /toggle_video"), 500

@video_bp.route('/video_feed')
@login_required
@url_required
def video_feed():
    try:
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /video_feed"), 500