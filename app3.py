#Docker container runnable file
from flask import Flask
from dotenv import load_dotenv
from waitress import serve # type: ignore
import os

load_dotenv()

app = Flask(
    __name__,
    static_folder="views/static",
    template_folder="views/templates"
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

from controllers.main_controller import main_bp
from controllers.video_controller import video_bp

app.register_blueprint(main_bp)
app.register_blueprint(video_bp)

if __name__ == '__main__':
    print("Server started at http://localhost:8087/")
    serve(app, host='0.0.0.0', port=8087) 