from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
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
socketio = SocketIO(async_mode='gevent', cors_allowed_origins="*", )

# Inisialisasi JWTManager
jwt = JWTManager()

def create_app():
    # Membuat aplikasi Flask
    app = Flask(__name__)

    # Mengaktifkan CORS
    CORS(app, supports_credentials=True)
    
    # Menambahkan konfigurasi database ke aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Konfigurasi session
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    Session(app)

    # Konfigurasi JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_SESSION_COOKIE"] = False  # Gunakan masa kedaluwarsa eksplisit untuk access token
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Access token berlaku 10 menit
    app.config["JWT_COOKIE_SECURE"] = False  # Ubah ke True jika HTTPS
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"  # Ubah ke "None" jika HTTPS

    # Menginisialisasi objek db dan socketio dengan aplikasi Flask
    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(JWTDecodeError)
    def handle_auth_error(e):
        print("Posisi errornya: ", e)
        print("terdeteksi akses tidak valid")
        return jsonify({"message": "Akses tidak valid"}), 401

    # @jwt.unauthorized_loader
    # def unauthorized_callback(callback):
    #     return jsonify({"message": "Unauthorized"}), 401

    # Inisialisasi migrasi database
    migrate = Migrate(app, db)

    @app.route('/test', methods=['GET'])
    def test_connection():
        return jsonify({"message": "Server is running"}), 200

    # Impor blueprint setelah inisialisasi db
    from .controllers.user_controller import user_controller
    app.register_blueprint(user_controller, url_prefix='/users')

    from .controllers.pdf_controller import pdf_controller
    app.register_blueprint(pdf_controller, url_prefix='/datasets')

    from .controllers.link_controller import link_controller
    app.register_blueprint(link_controller, url_prefix='/url-datasets')

    from .controllers.vectordb_controller import vectordb_controller
    app.register_blueprint(vectordb_controller, url_prefix='/vectordb')

    from .controllers.retriever_controller import retriever_controller
    app.register_blueprint(retriever_controller, url_prefix='/retriever')

    from .controllers.chat_history_controller import chat_history_controller
    app.register_blueprint(chat_history_controller, url_prefix='/chat-history')
    
    #  # Impor dan inisialisasi SocketIO dari file lain
    from .controllers.socket_controller import init_socket_event
    init_socket_event(socketio)

    # Impor models setelah db diinisialisasi untuk mencegah circular import
    from . import models

    return app
