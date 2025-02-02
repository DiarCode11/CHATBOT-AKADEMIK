from flask import Blueprint, request, jsonify, session, make_response
from ..models import Users, db, UserRole
from argon2 import PasswordHasher
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, JWTManager, unset_jwt_cookies
from functools import wraps

ph = PasswordHasher()
user_controller = Blueprint('user', __name__)
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator_view(*args, **kwargs):
            claims = get_jwt_identity()
            if claims['role'] != role:
                return jsonify({'message': 'Anda tidak memiliki izin untuk mengakses halaman ini'}), 403
            return fn(*args, **kwargs)
        return decorator_view
    return wrapper

# Endpoint untuk menampilkan semua user
@user_controller.route('/', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user():
    users = Users.query.all()
    return jsonify([user.username for user in users])

# Endpoint untuk menambahkan user
@user_controller.route('/register', methods=['POST'])
def add_user():
    data = request.get_json()

    print(data)

    if not data:
        return jsonify({'message': 'Data tidak boleh kosong'}), 400

    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'JSON tidak valid'}), 400
    
    if not data['username'] or not data['email'] or not data['password']:
        return jsonify({'message': 'Input tidak boleh kosong'}), 400
    
    if len(data['username']) < 4:
        return jsonify({'message': 'Nama lengkap minimal 4 karakter'}), 400
    
    if any(char.isdigit() for char in data['username']):
        return jsonify({'message': 'Nama lengkap tidak boleh berisi angka'}), 400
    
    if len(data['password']) < 8:
        return jsonify({'message': 'Password minimal 8 karakter'}), 400
    
    if data['password'] != data['confirmPassword']:
        return jsonify({'message': 'Password tidak sama'}), 400
    
    # Cek apakah merupakan email Undiksha
    if not (data['email'].endswith('@undiksha.ac.id') or not data['email'].endswith('@student.undiksha.ac.id')):
        return jsonify({'message': 'Email harus menggunakan domain @undiksha.ac.id'}), 400

    # Cek apakah email sudah terdaftar
    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'Email sudah terdaftar'}), 400

    password_hash = ph.hash(data['password'])
    new_user = Users(username=data['username'], email=data['email'], password=password_hash)
    
    try:
        db.session.add(new_user)
        db.session.commit()

        try:
            user = Users.query.filter_by(email=data['email']).first()
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['role'] = user.role

            # Membuat access token dengan user id dan role
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role.name}, expires_delta=False)

            # Kirimkan JSON data user
            response = jsonify({'message': 'Daftar berhasil', 'user': {'username': user.username, 'email': user.email, 'role': user.role.name}})

            # Set access token ke cookies
            set_access_cookies(response, access_token)

            # Tambahkan informasi user ke cookie
            response.set_cookie('username', user.username, max_age=60*60*24, httponly=False, samesite='Lax')
            response.set_cookie('role', user.role.name, max_age=60*60*24, httponly=False, samesite='Lax')
        
        except Exception as e:
            print("Error saat koneksi ke database: ", str(e))
            return jsonify({'message': 'Terjadi kesalahan di internal server'}), 500

        return response, 201
    
    except Exception as e:
        print("Error saat koneksi ke database: ", str(e))
        return jsonify({'message': 'Terjadi kesalahan di internal server'}), 

# Endpoint untuk login
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    print(data)

    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Input tidak valid'}), 400
    
    # Cek apakah merupakan email Undiksha
    if not (data['email'].endswith('@undiksha.ac.id') or data['email'].endswith('@student.undiksha.ac.id')):
        return jsonify({'message': 'Email harus menggunakan domain @undiksha.ac.id atau @student.undiksha.ac.id'}), 400

    user = Users.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Email belum terdaftar, silahkan daftar terlebih dahulu'}), 404
    
    try:
        ph.verify(user.password, data['password'])
        print("berhasil melalui tes pasword")
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email
        session['role'] = user.role

        # Membuat access token dengan user id dan role
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role.name}, expires_delta=False)

        # Kirimkan JSON data user
        response = jsonify({'message': 'Login berhasil', 'user': {'username': user.username, 'email': user.email, 'role': user.role.name}})

        # Set access token ke cookies
        set_access_cookies(response, access_token)

        # Tambahkan informasi user ke cookie
        response.set_cookie('username', user.username, max_age=60*60*24, httponly=False, samesite='Lax')
        response.set_cookie('role', user.role.name, max_age=60*60*24, httponly=False, samesite='Lax')

        print("berhasil melalui proses  validasi login")
        # Berikan response
        return response, 200
    
    except Exception as e:
        print("Error: ", str(e))
        return jsonify({'message': 'Email atau password salah'}), 400
    
@user_controller.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    session.clear()
    
    # Menghapus access token dari cookies
    response = make_response(jsonify({'message': 'Logout berhasil'}))
    unset_jwt_cookies(response)

    # Menghapus cookie dengan mengatur waktu kedaluwarsa ke waktu yang sudah lewat
    response.set_cookie('access_token', '', expires=0, httponly=True, samesite='Lax')
    response.set_cookie('username', '', expires=0, httponly=False, samesite='Lax')
    response.set_cookie('role', '', expires=0, httponly=False, samesite='Lax')

    print('logout berhasil')

    return response, 200

# Endpoint untuk menambahkan user oleh admin (Backpage)
@user_controller.route('/register-by-admin', methods=['POST'])
def add_user_by_admin():
    pass

@user_controller.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'JSON tidak valid'}), 400
    
    if not data['email'] or not data['password']:
        return jsonify({'message': 'Input tidak boleh kosong'}), 400
    
    # cek apakah yang menghapus adalah admin
    user_remover = Users.query.filter_by(email=data['email']).first()

    user_want_to_remove = Users.query.get(id)

    try:
        ph.verify(user_remover.password, data['password'])
    except Exception as e:
        return jsonify({'message': 'Email atau password salah'}), 401
    
    if user_remover.id == user_want_to_remove.id:
        return jsonify({'message': 'Anda tidak bisa menghapus diri sendiri'}), 403

    if user_remover.role != UserRole.admin:
        return jsonify({'message': 'Anda tidak memiliki izin untuk menghapus user'}), 403
    
    if user_remover.role != UserRole.admin:
        return jsonify({'message': 'Anda tidak memiliki izin untuk menghapus user'}), 403

    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User berhasil dihapus'}), 200

# @user_controller.route('/logout', methods=['POST'])
# def logout():
#     return jsonify({'message': 'Logout successful'}), 200