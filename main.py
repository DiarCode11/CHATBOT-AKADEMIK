from app import create_app, socketio
from flask import send_from_directory

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, use_reloader=True)


