# Gunakan image Python terbaru
FROM python:3.10

# Set direktori kerja dalam container
WORKDIR /app

# Salin semua file ke dalam container
COPY . .

# Expose port (sesuai dengan yang dipakai Flask/FastAPI)
EXPOSE 5001

# Install dependencies dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan aplikasi (ganti dengan file utama Python Anda)
CMD ["python", "main.py"]