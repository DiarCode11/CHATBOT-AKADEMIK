import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flasgger import Swagger
from graph import build_graph
from dotenv import load_dotenv
import os
import jwt

load_dotenv()
# Inisialisasi Flask dan Flask-SocketIO
app = Flask(__name__)
SECRET_KEY = os.getenv('SECRET_KEY')

# Menambahkan CORS untuk rute HTTP
CORS(app)

# Menambahkan Swagger
swagger = Swagger(app)

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

clients = []

def generate_token():
    payload = {
        # Tidak ada klaim 'exp' di sini
        'user': 'username',  # Misalnya menambahkan informasi pengguna jika perlu
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# REST API
@app.route('/api/login', methods=['POST'])
def login():
  # Kredensial Valid
  valid_email = os.getenv('LOGIN_EMAIL')
  valid_pass = os.getenv('LOGIN_PASSWORD')

  try:
    data = request.get_json()
    username = data['email']
    password = data['password']

    if 'email' not in data or 'password' not in data:
      return jsonify({'status': 'error', 'message': 'Parameter tidak ditemukan'}), 400
    if not username or not password:
      return jsonify({'status': 'error', 'message': 'Username atau password tidak boleh kosong'}), 400
    if username == valid_email and password == valid_pass:
      return jsonify({'status': 'success', 'message': 'Login berhasil'}), 200
    else:
      return jsonify({'status': 'error', 'message': 'Username atau password salah'}), 400
  except Exception as e:
    return jsonify({'status': 'error','message': 'Kesalahan JSON'}), 400

# SOCKET IO
@socketio.on('connect', namespace='/')
def handle_connect():
    clients.append(request.remote_addr)
    print(f"\n{len(clients)} Klien unik terhubung.")
    print(f"IP client terhubung: {str(clients)}")

    token = generate_token()

    emit('message', {'data': 'Selamat datang! Anda terhubung dengan WebSocket.'})

# Mengatur event untuk menangani disconnect
@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    print("\nKlien terputus.")
    clients.remove(request.remote_addr)
    print("Jumlah client terhubung (unique): ", len(set(clients)))
    print("IP client terhubung: ", str(clients))

@socketio.on('send_message')
def handle_message(data):
    socket_id = request.sid
    # Menangkap teks yang dikirimkan oleh klien
    print(f"ID klien: {socket_id}")
    print(f"Pesan dari klien: {data['message']}")
    query = data['message']  # Mengambil teks pesan yang dikirimkan

    full_response = build_graph(query)

    length_chars: int = 4

    for i in range(0, len(full_response), length_chars):
        chunk = full_response[i:i+length_chars]
        emit('response', {'data': chunk}, room=socket_id)
        eventlet.sleep(0.08)

# Menambahkan endpoint untuk dokumentasi Swagger
@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """
    Endpoint untuk chat
    ---
    tags:
      - Uji Response Akasha
    parameters:
      - name: input
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Siapa rektor undiksha"
    responses:
      200:
        description: Respons berhasil
        content:
          application/json:
            schema:
              type: object
    """
    data = request.json

    if not 'message' in data or data['message'] is None:
        return jsonify({'error': 'Parameter message tidak ditemukan'}), 400

    try:
        message = data['message']
        response = build_graph(message)
        return jsonify({'response': response}), 200

    except Exception as e:
        return jsonify({'error': 'Kesalahan internal server'}), 500

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, use_reloader=True)
