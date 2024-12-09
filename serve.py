from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from main import create_response
from flask_cors import CORS

# Inisialisasi Flask dan Flask-SocketIO
app = Flask(__name__)

# Menambahkan CORS untuk rute HTTP
CORS(app)

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")


clients = []
@socketio.on('connect', namespace='/')
def handle_connect():
    print("\nKlien terhubung.")
    clients.append(request.remote_addr)
    print("Jumlah client terhubung (unique): ", len(set(clients)))
    print("IP client terhubung: ", str(clients))

    emit('message', {'data': 'Selamat datang! Anda terhubung dengan WebSocket.'})

# Mengatur event untuk menangani disconnect
@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    print("\nKlien terputus.")
    clients.remove(request.remote_addr)
    print("Jumlah client terhubung (unique): ", len(set(clients)))
    print("IP client terhubung: ", str(clients))
    

# Rute HTTP untuk menguji koneksi (POST)
@app.route("/")
def home():
    return jsonify({"message": "Berhasil terhubung", "status": "success"}), 200

@app.route("/api", methods=["POST"])
def api():
    # Memastikan bahwa data yang diterima adalah JSON
    if request.is_json:
        # Mengambil data JSON yang dikirimkan oleh klien
        data = request.get_json()

        # Menampilkan data JSON
        print(data)

        # Memproses data JSON
        query = data["query"]

        print(f"Ini query pengguna: {query}")
        response = create_response(query)

        # Membuat respons yang akan dikirim balik ke klien
        response = {
            "response": response,
            "role": "assistant",
            "status": "success"
        }
        return jsonify(response), 200  # Mengembalikan respons dalam format JSON dengan status 200 OK
    else:
        return jsonify({"error": "Invalid JSON format"}), 400  # Jika format data bukan JSON, kirim error 400


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)