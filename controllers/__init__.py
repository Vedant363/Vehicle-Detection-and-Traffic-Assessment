from flask import Blueprint

# Example: import your blueprints from other modules
from .main_controller import main_bp
from .video_controller import video_bp

# (Optional) This blueprint is not strictly necessary if you are
# registering blueprints in app.py. You can import main_bp and video_bp
# directly into app.py instead.
controllers_bp = Blueprint('controllers', __name__)

# If you prefer, you may register main_bp and video_bp with controllers_bp here:
# controllers_bp.register_blueprint(main_bp)
# controllers_bp.register_blueprint(video_bp)