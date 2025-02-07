# Fungsi validasi JSON
def validate_json(data, required_keys):
    error_keys = []
    for key in required_keys:
      if key not in data:
        return f"Parameter {key} tidak ditemukan."
      if not data[key]:
        error_keys.append(key)
    if error_keys:
      return f"Parameter tidak boleh kosong.", error_keys

    return None, None

# Fungsi validasi file
def validate_file(file):
    if not file:
        return "Parameter file tidak ditemukan."
    if file.filename == '':
        return "File tidak memiliki nama."
    if not allowed_file(file.filename, ["pdf"]):
        return "File harus dalam format PDF."
    return None

# Fungsi untuk memeriksa ekstensi file
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions