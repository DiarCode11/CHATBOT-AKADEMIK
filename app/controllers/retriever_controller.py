from flask import Blueprint, request, jsonify, session
from ..models import LLMSetting, db
from datetime import datetime
import re

retriever_controller = Blueprint('retriever', __name__)

@retriever_controller.route('', methods=['GET'])
def get_latest_setting():
    latest_llm_setting = LLMSetting.query.order_by(LLMSetting.created_at.desc()).first()
    setting = latest_llm_setting.to_dict() if latest_llm_setting else None

    if not setting:
        return jsonify({"message": "Pengaturan LLM tidak ditemukan, mohon tambahkan pengaturan LLM"}), 404
    
    return jsonify({"message": "Pengaturan terbaru ditemukan", "data": setting}), 200

@retriever_controller.route('', methods=['POST'])
def add_new_setting():
    data = request.get_json()

    llm_list = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]

    if not data:
        return jsonify({"message": "parameter tidak boleh kosong"}), 400
    
    if "llm" not in data:
        return jsonify({"message": "Parameter diharapkan: 'llm'"}), 400
    
    if "k" not in data:
        return jsonify({"message": "Parameter diharapkan: 'k'"}), 400
    
    if not data['llm'] or not data['k']:
        return jsonify({"message": "Data tidak boleh kosong"}), 400
    
    if data["llm"] not in llm_list:
        return jsonify({"message": "model llm tidak valid"}), 400
    
    try:
        k = int(data['k'])
    except:
        return jsonify({"message": "Nilai kandidat harus angka"})
    
    if data['k'] < 5 or data['k'] > 20:
        return jsonify({"message": "Rentang nilai kandidat harus 5-20"})
    
    new_setting = LLMSetting(
        llm = data['llm'],
        candidates_size = data['k'],
        created_user_id = '53c3b91f-3946-4e63-be22-663f331a0b77',
        created_at = datetime.now()
    )    

    try:
        db.session.add(new_setting)
        db.session.commit()
        return jsonify({"message": "Pengaturan berhasil tersimpan", "data": new_setting.to_dict()}), 201
    except Exception as e:
        print(str(e))
        return jsonify({"message": "Gagal menyimpan data ke database"}), 500
    
    
    
    




