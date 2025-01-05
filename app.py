# Local machine runnable file
from flask import Flask
from dotenv import load_dotenv
from waitress import serve  # type: ignore
import os

load_dotenv()

# Specify custom paths for static and templates directories
app = Flask(
    __name__,
    static_folder="views/static",
    template_folder="views/templates"
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

from models.decryption import decrypt_file  
decrypt_file()  

from controllers.main_controller import main_bp
from controllers.video_controller import video_bp

app.register_blueprint(main_bp)
app.register_blueprint(video_bp)

if __name__ == '__main__':
    app.run()
