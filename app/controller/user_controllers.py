from flask import Blueprint, request, jsonify, session
from ..models import Users, db, UserRole
from argon2 import PasswordHasher
from email_validator import validate_email, EmailNotValidError

ph = PasswordHasher()

user_controller = Blueprint('user', __name__)

# Endpoint untuk menampilkan semua user
@user_controller.route('/', methods=['GET'])
def get_user():
    users = Users.query.all()
    return jsonify([user.username for user in users])

# Endpoint untuk menambahkan user
@user_controller.route('/register', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'JSON tidak valid'}), 400
    
    if not data['username'] or not data['email'] or not data['password']:
        return jsonify({'message': 'Input tidak boleh kosong'}), 400
    
    # Cek apakah merupakan email Undiksha
    if not (data['email'].endswith('@undiksha.ac.id') or not data['email'].endswith('@student.undiksha.ac.id')):
        return jsonify({'message': 'Email harus menggunakan domain @undiksha.ac.id'}), 400

    # Cek apakah email sudah terdaftar
    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'Email sudah terdaftar'}), 400

    password_hash = ph.hash(data['password'])
    new_user = Users(username=data['username'], email=data['email'], password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User berhasil terdaftar', 'user': {'username': new_user.username, 'email': new_user.email}})

# Endpoint untuk login
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Cek apakah merupakan email Undiksha
    if not data['email'].endswith('@undiksha.ac.id') or not data['email'].endswith('@student.undiksha.ac.id'):
        return jsonify({'message': 'Email harus menggunakan domain @undiksha.ac.id'}), 400

    user = Users.query.filter_by(email=data['email']).first()
    if user and ph.verify(user.password, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email
        session['role'] = user.role
        return jsonify({'message': 'Login successful', 'user': {'username': user.username, 'email': user.email}}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

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

@user_controller.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200