# BACKEND CHATBOT GENERATIVE AI AKASHA

Ini merupakan projek Chatbot Generative AI Akasha untuk informasi akademik Undiksha. Chatbot ini menerapkan pendekatan Corrective-RAG untuk membangun chatbot yang interaktif dengan menggunakan dokumen akademik Undiksha sebagai basis pengetahuan. Backend ini menggunakan **RESTful API** dan **Socket.IO** yang dibangun dengan **Flask** untuk mendukung pengelolaan data dataset pada aplikasi Chatbot Akademik. Proyek ini merupakan bagian dari penelitian/skripsi yang bertujuan mengintegrasikan berbagai sumber data (PDF dan link) ke dalam sistem chatbot yang cerdas dan responsif.

## Fitur Utama
- **Manajemen Dataset PDF**  
  - Mengambil, menambah, memperbarui, dan menghapus data dataset PDF.
  
- **Manajemen Dataset Link**  
  - Mengambil, menambah, memperbarui, dan melakukan scraping pada data dataset berbasis URL.
  
- **Otentikasi dan Autorisasi**  
  - Menggunakan **JWT (JSON Web Tokens)** untuk mengamankan endpoint API.
  - Implementasi **role-based authorization** dengan custom decorator `role_required` untuk membatasi akses (misalnya, hanya admin yang dapat mengakses endpoint tertentu).
  
- **Realtime Communication**  
  - Integrasi dengan **Flask-SocketIO** untuk mendukung komunikasi realtime (opsional).

- **Database Terintegrasi**  
  - Menggunakan **SQLAlchemy** dan **Flask-Migrate** untuk manajemen database MySQL.
  
- **Session & CORS**  
  - Mengaktifkan **Flask-Session** untuk manajemen sesi dan **Flask-CORS** untuk mendukung permintaan dari berbagai domain.

## Instalasi
1. **Clone Repository:**
```bash
git clone https://github.com/username/chatbot-akademik.git
cd chatbot-akademik
```
2. **Buat Virtual Environment dan Install Dependencies:**
```bash
# Buat virtual environment
python -m venv akasha_env

# Aktifkan virtual environment
# Windows:
akasha_env\Scripts\activate
# Linux/Mac:
source akasha_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```
3. **Konfigurasi Environment Variable**
- Buat file .env di root project dan isikan konfigurasi berikut:
```env
# DATABASE CREDENTIALS
DB_USERNAME="root"
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
DB_NAME=""

# LLM CREDETIALS
OPENAI_API_KEY=""
EMBEDDING_MODEL=""
```
4. **Migrasi Database**
- Jalankan perintah migrasi untuk menginisialisasi dan memperbarui skema database:

```bash
flask db init
flask db migrate
flask db upgrade
```
5. **Jalankan server**
```bash
python main.py
```
# Kontribusi
Kontribusi sangat kami hargai! Jika kamu ingin memberikan perbaikan atau fitur baru, silakan fork repository ini, buat branch baru untuk fitur yang diinginkan, dan ajukan pull request. Jika menemukan bug atau memiliki saran, jangan ragu untuk membuka issue.
