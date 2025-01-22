import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flasgger import Swagger
from graph import build_graph
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from tools.api_tools import check_is_allowed, validate_file, validate_json
from datetime import datetime
import pandas as pd
from tools.indexing_langchain import create_db_with_langchain
import os
import jwt
import uuid

load_dotenv()
# Inisialisasi Flask dan Flask-SocketIO
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload_docs'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_EXTENSIONS = {'pdf'}

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

@app.route('/api/dataset-management', methods=['GET'])
def get_dataset():
  try:
    df = pd.read_csv("dataset/pdf_list.csv")

    df_list = []

    for index, row in df.iterrows():
      df_list.append(row.to_dict())

    return jsonify({"status": "success", "data": df_list}), 200
  
  except Exception as e:
    return jsonify({"status": "failed", "data": None}), 400
      
@app.route('/api/dataset-management', methods=['POST'])
def store():
    # Baca data CSV
    try:
      dtype = {
          "id": "string",          # ID biasanya berupa string unik
          "file": "string",    # Nama file juga berupa string
          "filetype": "string",    # Tipe file biasanya berupa string (contoh: "pdf", "docx")
          "year": "int64",         # Tahun adalah angka, jadi gunakan tipe integer
          "created_at": "string",  # Tanggal biasanya diawali sebagai string (nanti bisa diubah ke datetime)
          "updated_at": "string"   # Sama seperti created_at, awalnya string
      }
      df = pd.read_csv("dataset/pdf_list.csv", dtype=dtype)
    except FileNotFoundError:
      return jsonify({"status": "failed", "message": "Database tidak ditemukan"}), 500
    
    file = request.files.get('file')

    if not file:
      return jsonify({"status": "failed", "message": "Parameter file tidak ditemukan"}), 400
    
    filename = secure_filename(file.filename)

    # Ambil JSON dari form-data
    data = {
        "file": filename,
        "filetype": request.form.get('filetype'),
        "year": request.form.get('year')
    }

     # Validasi apakah data JSON lengkap
    json_error, null_keys = validate_json(data, ['file', 'year'])
    print("Isi error json: ", json_error)
    if json_error:
      return jsonify({"status": "failed", "message": json_error, "null_keys": null_keys}), 400

    # Validasi file
    file_error = validate_file(file)
    if file_error:
      return jsonify({"status": "failed", "message": file_error}), 400
    
    # Jika Validasi telah selesai
    new_data = {
      "id": str(uuid.uuid4()),
      "file": data["file"],
      "filetype": data["filetype"],
      "year": int(data["year"]),
      "created_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
      "updated_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }

    # Tambahkan data ke baris baru
    df.loc[len(df)] = new_data

    # Simpan file
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Buat folder jika belum ada
    file.save(upload_path)
  
    # Simpan kembali ke file CSV
    df.to_csv("dataset/pdf_list.csv", index=False)

    # Response dengan JSON
    return jsonify({"status": "success", "message": "Data berhasil ditambahkan"}), 201

@app.route('/api/dataset-management/<id>', methods=['PUT'])
def update(id):
    # Baca data CSV
    try:
        dtype = {
            "id": "string",          # ID biasanya berupa string unik
            "file": "string",    # Nama file juga berupa string
            "filetype": "string",    # Tipe file biasanya berupa string (contoh: "pdf", "docx")
            "year": "int64",         # Tahun adalah angka, jadi gunakan tipe integer
            "created_at": "string",  # Tanggal biasanya diawali sebagai string (nanti bisa diubah ke datetime)
            "updated_at": "string"   # Sama seperti created_at, awalnya string
        }
        df = pd.read_csv("dataset/pdf_list.csv", dtype=dtype)
    except FileNotFoundError:
        return jsonify({"status": "failed", "message": "Database tidak ditemukan"}), 500

    # Validasi ID
    if id not in df['id'].values:
        return jsonify({"status": "failed", "message": "ID tidak valid"}), 400

    # Ambil data form
    try:
        file = request.files.get('file')
        old_df_row = df.loc[df['id'] == id].to_dict(orient='records')[0]
        print(old_df_row["file"])
  
        if not file:
          return jsonify({"status": "failed", "message": "Parameter file tidak ditemukan"}), 400
        
        filename = secure_filename(file.filename)

        # Ambil JSON dari form-data
        data = {
            "file": filename,
            "filetype": request.form.get('filetype'),
            "year": request.form.get('year')
        }

        print("Isi data: ", data)

        # Validasi apakah data JSON lengkap
        json_error, null_keys = validate_json(data, ['file', 'filetype', 'year'])
        print("Isi error json: ", json_error)
        if json_error:
            return jsonify({"status": "failed", "message": json_error, "null_keys": null_keys}), 400

        # Validasi file
        file_error = validate_file(file)
        if file_error:
            return jsonify({"status": "failed", "message": file_error}), 400
        
        try:
          # Perbarui data pada DataFrame
          df.loc[df['id'] == id, 'file'] = data['file']
          df.loc[df['id'] == id, 'filetype'] = data['filetype']
          df.loc[df['id'] == id, 'year'] = int(data['year'])
          df.loc[df['id'] == id, 'updated_at'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

          # Simpan kembali ke file CSV
          df.to_csv("dataset/pdf_list.csv", index=False)

          # Hapus file lama
          os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_df_row['file']))

          # Simpan file
          upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Buat folder jika belum ada
          file.save(upload_path)
        except Exception as e:
          return jsonify({"status": "failed", "message": f"format JSON salah {str(e)}"}), 400

        return jsonify({"status": "success", "message": "Data berhasil diupdate"}), 200
    except Exception as e:
        return jsonify({"status": "failed", "message": f"Kesalahan internal server: {str(e)}"}), 500

@app.route('/api/dataset-management/<id>', methods=['DELETE'])
def delete(id):
  # Baca data CSV
  try:
    dtype = {
        "id": "string",          # ID biasanya berupa string unik
        "file": "string",    # Nama file juga berupa string
        "filetype": "string",    # Tipe file biasanya berupa string (contoh: "pdf", "docx")
        "year": "int64",         # Tahun adalah angka, jadi gunakan tipe integer
        "created_at": "string",  # Tanggal biasanya diawali sebagai string (nanti bisa diubah ke datetime)
        "updated_at": "string"   # Sama seperti created_at, awalnya string
    }

    df = pd.read_csv("dataset/pdf_list.csv", dtype=dtype)
  except FileNotFoundError:
    return jsonify({"status": "failed", "message": "Database tidak ditemukan"}), 500
  
  # Validasi ID
  if id not in df['id'].values:
    return jsonify({"status": "failed", "message": "ID tidak valid"}), 400
  
  try:
    old_df_row = df.loc[df['id'] == id].to_dict(orient='records')[0]
    # Hapus file dan baris dengan parameter id
    df = df[df["id"] != id]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_df_row['file'])

    if os.path.exists(file_path):
        # Hapus file jika ada
        os.remove(file_path)

    # Simpan kembali ke file CSV
    df.to_csv("dataset/pdf_list.csv", index=False)

    # Response dengan JSON
    return jsonify({"status": "success", "message": "Data berhasil dihapus"}), 200
  
  except Exception as e:
    return jsonify({"status": "failed", "message": "Kesalahan internal server"}), 500
  
@app.route('/api/generate-db', methods=['POST'])
def generate_vectordb():
  # Daftar parameter yang diizinkan
  allowed_params = {'chunk_size', 'chunk_overlap'}
  
  # Ambil kunci parameter dari form-data
  received_params = set(request.form.keys())

  # Ambil JSON dari form-data
  if 'chunk_size' not in request.form or 'chunk_overlap' not in request.form:
    return jsonify({"status": "failed", "message": "Parameter chunk_size dan chunk_overlap harus ada"}), 400
  
  # Periksa apakah parameter yang diterima sesuai dengan yang diizinkan
  if not allowed_params.issubset(received_params) or len(received_params - allowed_params) > 0:
    return jsonify({"status": "failed", "message": "Hanya parameter 'chunk_size' dan 'chunk_overlap' yang diperbolehkan"}), 400

  
  if not request.form.get("chunk_size") or not request.form.get("chunk_overlap"):
    return jsonify({"status": "failed", "message": "Parameter chunk_size atau chunk_overlap tidak boleh kosong"}), 400

  data = {
     "chunk_size": request.form.get("chunk_size"),
     "chunk_overlap": request.form.get("chunk_overlap")
  }

  try:
    chunk_size = int(data['chunk_size'])
    chunk_overlap = int(data['chunk_overlap'])

    if chunk_size <= 0 or chunk_overlap <= 0:
      return jsonify({"status": "failed", "message": "Chunk size atau chunk overlap harus lebih besar dari 0"}), 400
    
    try:
      create_db_with_langchain(chunk_size, chunk_overlap)
      return jsonify({"status": "success", "message": "Database berhasil dibuat"}), 200
    except Exception as e:
      return jsonify({"status": "failed", "message": "Kesalahan internal server"}), 500
    
  except Exception as e:
    return jsonify({"status": "failed", "message": "Chunk size atau chunk overlap harus angka"}), 400

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
