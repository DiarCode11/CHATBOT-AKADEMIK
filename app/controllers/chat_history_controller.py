from flask import Blueprint, request, jsonify, session
from ..models import ChatProcess, LLMSetting, db
from datetime import datetime
from flask_jwt_extended import jwt_required
from ..utils.authorization import role_required
import math

chat_history_controller = Blueprint('chat_history', __name__)

@jwt_required()
@role_required('admin')
@chat_history_controller.route('/chat', methods=['GET'])
def get_chat_history():
    print("Chat diakses")
    try:
        page = request.args.get('page', default=1, type=int)

        try:
            page = int(page)
            print(page)
        except ValueError:
            return jsonify({"message": "Parameter page harus berupa angka", "data": []}), 400

        if page < 0:
            return jsonify({"message": "Parameter page tidak boleh kurang dari 1", "data": []}), 400

        items_per_page = 5
        data_chat = ChatProcess.query.order_by(ChatProcess.created_at.desc()).paginate(
            page=page, per_page=items_per_page, error_out=False
        ).items

        total_data = ChatProcess.query.count()

        if total_data == 0:
            return jsonify({"message": "Data chat kosong", "data": []}), 404
        
        total_page = math.ceil(total_data / items_per_page)

        if page > total_page:
            return jsonify({"message": "Halaman tidak ditemukan", "data": []}), 404

        all_data = [data_chat.to_dict() for data_chat in data_chat]

        return jsonify({"message": "data berhasil diambil", "data": all_data, "total_page": total_page, "current_page": page, "items_per_page": items_per_page, "total_data": total_data}), 200
    except Exception as e:
        print("Error saat mengakses pengaturan: ", str(e))
        return jsonify({"message": "Gagal dalam mengakses pengaturan ", "data": all_data, "total_page": total_page, "current_page": page}), 500

@jwt_required()
@role_required('admin')
@chat_history_controller.route('/setting', methods=['GET'])
def get_last_setting():
    print("Setting diakses")
    latest_llm_setting = LLMSetting.query.order_by(LLMSetting.created_at.desc()).first()
    setting = latest_llm_setting.to_dict()

    if not setting:
        return jsonify({"message": "Pengaturan LLM tidak ditemukan, mohon tambahkan pengaturan LLM"}), 404

    return jsonify({"message": "Pengaturan terbaru ditemukan", "data": setting}), 200

@jwt_required()
@role_required('admin')
@chat_history_controller.route('/setting', methods=['POST'])
def add_new_setting():
    data = request.get_json()
    print("Setting diakses")
    print("isi data", data)

    llm_list = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]

    llm = data.get('llm', None)
    candidate_size = data.get('candidate_size', None)

    if not data:
        return jsonify({"message": "parameter tidak valid, key 'llm' dan 'candidate_size' diperlukan"}), 400
    
    if not candidate_size:
        return jsonify({"message": "kandidat tidak boleh kosong"}), 400
    
    if not llm:
        return jsonify({"message": "model llm tidak boleh kosong"}), 400
    
    if not data.get('llm') or not data.get('candidate_size'):
        return jsonify({"message": "parameter tidak boleh kosong"}), 400
    
    try:
        candidate_size = int(candidate_size)
        if candidate_size < 1:
            return jsonify({"message": "kandidat harus lebih dari 0"}), 400
        if candidate_size > 20:
            return jsonify({"message": "kandidat tidak boleh lebih dari 20"}), 400
    except ValueError:
        return jsonify({"message": "kandidat harus berupa angka"}), 400

    if llm not in llm_list:
        return jsonify({"message": "llm tidak valid"}), 400
    
    user_id = '53c3b91f-3946-4e63-be22-663f331a0b77' # Wajib diganti dengan user id yang valid
    try:
        new_setting = LLMSetting(llm=llm, candidates_size=candidate_size, created_user_id=user_id, created_at=datetime.now())
        db.session.add(new_setting)
        db.session.commit()
        return jsonify({"message": "Pengaturan berhasil diubah", "data": new_setting.to_dict()}), 201
    except Exception as e:
        print("Error saat menambahkan pengaturan: ", str(e))
        return jsonify({"message": "Gagal dalam menambahkan pengaturan"}), 500
    


