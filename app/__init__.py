from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_session import Session
from datetime import timedelta
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Mendapatkan konfigurasi dari environment variables
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

# Membuat string URI untuk database
DB_URI = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Inisialisasi objek SQLAlchemy dan SocketIO
db = SQLAlchemy()
socketio = SocketIO()

# Inisialisasi JWTManager
jwt = JWTManager()

def create_app():
    # Membuat aplikasi Flask
    app = Flask(__name__)
    
    # Menambahkan konfigurasi database ke aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Konfigurasi session
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    Session(app)

    # Menginisialisasi objek db dan socketio dengan aplikasi Flask
    db.init_app(app)
    socketio.init_app(app)

    # Inisialisasi migrasi database
    migrate = Migrate(app, db)

    # # Middleware untuk membatasi akses tanpa session
    # @app.before_request
    # def restrict_to_session():
    #     # Pastikan pengguna memiliki session valid
    #     if request.endpoint not in ['user.login', 'static'] and 'user_id' not in session:
    #         return jsonify({'message': 'Unauthorized access. Please login first.'}), 401

    # Impor blueprint setelah inisialisasi db
    from .controller.user_controllers import user_controller
    app.register_blueprint(user_controller, url_prefix='/users')

    # Impor models setelah db diinisialisasi untuk mencegah circular import
    from . import models

    return app
