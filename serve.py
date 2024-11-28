from flask import Flask, request, jsonify
from main import create_response


app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello, Flask!</h1><p>Welcome to your first Flask application.</p>"

@app.route("/api", methods=["POST"])
def api():
    # Memastikan bahwa data yang diterima adalah JSON
    if request.is_json:
        # Mengambil data JSON yang dikirimkan oleh klien
        data = request.get_json()
        
        # Memproses data JSON
        query = data["query"]
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
    app.run(debug=True)
