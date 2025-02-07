import gevent
from flask_socketio import SocketIO, emit
from flask import Flask, request, jsonify, session
from graph import build_graph
from .. import socketio

# Membuat instance SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def init_socket_event(socketio):
    clients = []

    @socketio.on('connect', namespace='/')
    def handle_connect():
        clients.append(request.remote_addr)
        print(f"\n{len(set(clients))} Klien unik terhubung.")
        user_amount = len(set(clients))
        print(f"IP client terhubung: {str(set(clients))}")
        emit('user_connected', {'amount': user_amount, 'message': 'klien terhubung'}, broadcast=True)

    @socketio.on('disconnect', namespace='/')
    def handle_disconnect():
        print("\nKlien terputus.")
        clients.remove(request.remote_addr)
        print("Jumlah client terhubung (unique): ", len(set(clients)))
        print("IP client terhubung: ", str(clients))
        user_amount = len(set(clients))
        emit('user_disconnected', {'amount': user_amount, 'message': 'klien terputus'}, broadcast=True)

    @socketio.on('send_message')
    def handle_message(data):
        socket_id = request.sid
        # Menangkap teks yang dikirimkan oleh klien
        print(f"ID klien: {socket_id}")
        print(f"Pesan dari klien: {data['message']}")
        query = data['message']  # Mengambil teks pesan yang dikirimkan

        try:
            full_response = build_graph(query)

            length_chars: int = 4

            for i in range(0, len(full_response), length_chars):
                chunk = full_response[i:i+length_chars]
                emit('response', {'chunk': chunk}, room=socket_id)
                gevent.sleep(0.08)

        except Exception as e:
            print('Terdapat error ', str(e))
            error_response = "Sepertinya ada masalah dengan internal server. Mohon tunggu beberapa saat untuk maintenance"
            
            length_chars: int = 4

            for i in range(0, len(error_response), length_chars):
                chunk = error_response[i:i+length_chars]
                emit('response', {'chunk': chunk}, room=socket_id)
                gevent.sleep(0.08)