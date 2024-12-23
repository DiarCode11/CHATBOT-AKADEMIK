import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flasgger import Swagger
from graph import build_graph

# Inisialisasi Flask dan Flask-SocketIO
app = Flask(__name__)

# Menambahkan CORS untuk rute HTTP
CORS(app)

# Menambahkan Swagger
swagger = Swagger(app)

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

clients = []

@socketio.on('connect', namespace='/')
def handle_connect():
    clients.append(request.remote_addr)
    print(f"\n{len(clients)} Klien unik terhubung.")
    print(f"IP client terhubung: {str(clients)}")

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
    socketio.run(app, host="0.0.0.0", port=5000, use_reloader=True)
