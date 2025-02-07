from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator_view(*args, **kwargs):
            claims = get_jwt()
            print("Isi klaim: ", claims)
            if claims['role'] != role:
                return jsonify({'message': 'Anda tidak memiliki izin untuk mengakses halaman ini', 'status': False}), 403
            return fn(*args, **kwargs)
        return decorator_view
    return wrapper