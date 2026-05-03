#Ngrok runnable file
from flask import Flask
from flask_ngrok import run_with_ngrok
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(
    __name__,
    static_folder="views/static",
    template_folder="views/templates"
)

run_with_ngrok(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

from models.decryption import decrypt_file  
decrypt_file() 

from models.sheets import get_service_account_file
SERVICE_ACCOUNT_FILE = get_service_account_file()

from controllers.main_controller import main_bp
from controllers.video_controller import video_bp

app.register_blueprint(main_bp)
app.register_blueprint(video_bp)

if __name__ == '__main__':
    app.run()