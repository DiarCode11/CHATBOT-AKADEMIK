from flask import Blueprint, request, jsonify, session, make_response
from ..models import Users, db, UserRole, ModifiedDataset
from argon2 import PasswordHasher
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, set_access_cookies, unset_jwt_cookies, get_jwt_identity
from functools import wraps
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func, case
from ..utils.authorization import role_required

ph = PasswordHasher()
user_controller = Blueprint('user', __name__)

# Endpoint untuk menampilkan semua user
@user_controller.route('/all', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_user():
    users_query = Users.query.with_entities(
        Users,
        func.count(
            case((func.date(Users.created_at) == date.today(), 1))
        ).over().label("new_users_login")
    ).filter(Users.deleted_at == None).order_by(Users.created_at.desc()).all()

    # Ekstrak hasil
    users_list = []
    new_users_login = 0

    for row in users_query:
        users_list.append(row[0].to_dict())  # Ambil objek Users & konversi ke dict
        new_users_login = row[1] 

    if not users_list:
        return jsonify({'message': 'User tidak ditemukan'}), 404

    return jsonify({'message': 'Berhasil menampilkan semua user','data': users_list, 'new_users_login': new_users_login}), 200

@user_controller.route('/auth', methods=['GET'])
@jwt_required(locations=['cookies'])
def check_auth():
    identity = get_jwt()
    try:
        user_data = Users.query.filter_by(id=identity['sub'], deleted_at=None).first()

        user_dict = user_data.to_dict()

        print("Isi user data: ", user_dict['username'])

        if not user_data:
            return jsonify({'message': 'User tidak ditemukan'}), 404

        print("Isi identity: ", identity)
        return jsonify({'message': 'User terautentikasi', 'username': user_dict['username'], 'role': user_dict['role'], 'id': user_dict['id']}), 200
    
    except Exception as e:
        print("Posisi error", e)
        return jsonify({'message': 'Terdapat masalah ketika mengakses database'}), 500

@user_controller.route('/admin', methods=['POST'])
@jwt_required()
@role_required('admin')
def check_admin():
    return jsonify({'message': 'Anda terautentikasi sebagai admin', 'status': True}), 200

@user_controller.route('/add', methods=['POST'])
def add_user_by_admin():
    data = request.get_json()
    print("Berhasil mengakses endpoint add user by admin")

    name = data.get('name', None)
    email = data.get('email', None)
    password = data.get('password', None)
    role = data.get('role', None)

    key_list = ['name', 'email', 'role', 'password', 'confirmedPassword']
    role_list = ['admin', 'user']

    if not data:
        return jsonify({'message': 'Data tidak boleh kosong'}), 400

    for key in key_list:
        key_data = data.get(key, None)
        # Jika data ditemukan
        if key_data:
            if key == 'name':
                if len(key_data) < 4:
                    return jsonify({'message': 'Nama lengkap minimal 4 karakter'}), 400
                if any(char.isdigit() for char in key_data):
                    return jsonify({'message': 'Nama lengkap tidak boleh berisi angka'}), 400
            elif key == 'email':
                try:
                    validate_email(key_data)

                    try:
                        user_data = Users.query.filter_by(email=key_data, deleted_at=None).first()
                        if user_data:
                            return jsonify({'message': 'Email sudah terdaftar'}), 400
                    except Exception as e:
                        return jsonify({'message': 'Terjadi kesalahan internal server'}), 500
                    
                except EmailNotValidError as e:
                    return jsonify({'message': 'Email tidak valid'}), 400
                
                if (not key_data.endswith('@undiksha.ac.id')) and (not key_data.endswith('@student.undiksha.ac.id')):
                    return jsonify({'message': 'Email harus menggunakan domain @undiksha.ac.id atau @student.undiksha.ac.id'}), 400
            elif key == 'role':
                if key_data not in role_list:
                    return jsonify({'message': 'Role tidak valid'}), 400
            elif key == 'password':
                if len(key_data) < 8:
                    return jsonify({'message': 'Password minimal 8 karakter'}), 400
            elif key == 'confirmedPassword':
                if key_data != password:
                    return jsonify({'message': 'Password tidak sama'}), 400

        # Jika data tidak ditemukan
        if not key_data:
            if key == 'name':
                return jsonify({'message': 'Nama lengkap tidak boleh kosong'}), 400
            elif key == 'email':
                return jsonify({'message': 'Email tidak boleh kosong'}), 400
            elif key == 'role':
                return jsonify({'message': 'Role tidak boleh kosong'}), 400
            elif key == 'password':
                return jsonify({'message': 'Password tidak boleh kosong'}), 400
            elif key == 'confirmedPassword':
                return jsonify({'message': 'Konfirmasi password tidak boleh kosong'}), 400

    try:
        password_hash = ph.hash(password)
        new_user = Users(
            username = name, 
            email = email, 
            password=password_hash,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        db.session.add(new_user)
        db.session.commit()
        users_query = Users.query.with_entities(
            Users,
            func.count(
                case((func.date(Users.created_at) == date.today(), 1))
            ).over().label("new_users_login")
        ).filter(Users.deleted_at == None).order_by(Users.created_at.desc()).all()

        # Ekstrak hasil
        users_list = []
        new_users_login = 0

        for row in users_query:
            users_list.append(row[0].to_dict())  # Ambil objek Users & konversi ke dict
            new_users_login = row[1]  # Ambil jumlah user baru (sama untuk semua baris) 

        return jsonify({'message': 'User berhasil ditambahkan', 'data': users_list, 'new_users_login': new_users_login}), 200   
    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan internal server'}), 500
    

# Endpoint untuk menambahkan user
@user_controller.route('/register', methods=['POST'])
def register():
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
    new_user = Users(
        username=data['username'], 
        email=data['email'], 
        password=password_hash,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
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
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role.name, 'username': user.username, 'id': user.id}, expires_delta=False)

            # Kirimkan JSON data user
            response = jsonify({'message': 'Daftar berhasil', 'user': {'username': user.username, 'role': user.role.name}, 'auth': True})

            # Set access token ke cookies
            set_access_cookies(response, access_token)

            # # Tambahkan informasi user ke cookie
            # response.set_cookie('username', user.username, max_age=60*60*24, httponly=False, samesite='Lax')
            # response.set_cookie('role', user.role.name, max_age=60*60*24, httponly=False, samesite='Lax')
        
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
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role.name, 'username': user.username, 'id': user.id}, expires_delta=False)

        # Kirimkan JSON data user
        response = jsonify({'message': 'Login berhasil', 'user': {'username': user.username, 'email': user.email, 'role': user.role.name}, 'auth': True})

        # Set access token ke cookies
        set_access_cookies(response, access_token)

        # # Tambahkan informasi user ke cookie
        # response.set_cookie('username', user.username, max_age=60*60*24, httponly=False, samesite='Lax')
        # response.set_cookie('role', user.role.name, max_age=60*60*24, httponly=False, samesite='Lax')

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
    response = make_response(jsonify({'message': 'Logout berhasil', 'auth': False}))
    unset_jwt_cookies(response)

    # Menghapus cookie dengan mengatur waktu kedaluwarsa ke waktu yang sudah lewat
    response.set_cookie('access_token', '', expires=0, httponly=True, samesite='Lax')
    response.set_cookie('username', '', expires=0, httponly=False, samesite='Lax')
    response.set_cookie('role', '', expires=0, httponly=False, samesite='Lax')

    print('logout berhasil')

    return response, 200

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