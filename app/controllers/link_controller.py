from flask import Blueprint, request, jsonify, session, make_response
from ..models import UrlDatasets, ModifiedDataset, FileType, Action, db
from tools.api_tools import validate_file, validate_json
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, set_access_cookies, unset_jwt_cookies
from datetime import datetime
from ..utils.authorization import role_required
from ..utils.form_validation import *
from ..utils.scraper import scrape, remove_non_ascii
from sqlalchemy import func
import os
import uuid

link_controller = Blueprint('link', __name__)

@jwt_required()
@role_required('admin')
@link_controller.route('/link', methods=['GET'])
def get_link_dataset():
    try:
        dataset = UrlDatasets.query.filter(UrlDatasets.deleted_at.is_(None)).all()
        print(dataset)

        result = [
            {
                "id": data.id,
                "url": data.url,
                "title": data.title,
                "year": data.year,
                "extracted_text": data.extracted_text,
                "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": data.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for data in dataset
        ]

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.url) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_url = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_url_list = [data.to_dict() for data in not_updated_url]

        return jsonify({"status": "success", "data": result, "not_updated_url": not_updated_url_list}), 200
    
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat mengambil data"}), 500

@jwt_required
@role_required('admin')
@link_controller.route('/link/scrap', methods=['POST'])
def scrap_url():
    data = request.get_json()

    if ("link" not in data) or not data["link"]:
        return jsonify({"status": "failed", "message": "Data yang dikirimkan tidak boleh kosong"}), 400
    
    if not validate_link(data['link']):
        return jsonify({"status": "failed", "message": "URL tidak valid"}), 400

    response, scraping_data = scrape(data['link'])

    if response["status"] == "success":
        return jsonify({"status": "success", "message": response["message"], "data": scraping_data}), 200

    return jsonify({"status": "failed", "message": response["message"]}), 400

@jwt_required
@role_required('admin')
@link_controller.route('/link', methods=['POST'])
def add_link_dataset():
    data = request.get_json()
    print("Data yang didapatkan: ", data)

    # 1. Cek JSON kosong?
    if not data:
        return jsonify({"status": "failed", "message": "Data yang dikirimkan tidak boleh kosong"}), 400
    
    # 2. Cek setiap key ada
    if ("title" not in data) or ("link" not in data) or ("year" not in data) or ("text_scraped" not in data):
        return jsonify("Format data yang dikirimkan tidak sesuai"), 400
    
    if not data["title"] or not data["link"] or not data["year"]:
        return jsonify({"status": "failed", "message": "Data tidak boleh kosong"}), 400

    if not validate_title(data['title']):
        return jsonify({"status": "failed", "message": "Judul tidak boleh menggunakan karakter simbol"}), 400
    
    if len(data['title']) < 5 or len(data['title']) > 100:
        return jsonify({"status": "failed", "message": "Judul harus mengandung 5-20 karakter"}), 400
    
    if not data["link"]:
        return jsonify({"status": "failed", "message": "Link/url tidak boleh kosong"}), 400
    
    if not data["year"]:
        return jsonify({"status": "failed", "message": "Tahun tidak boleh kosong"}), 400
    
    if not validate_link(data['link']):
        return jsonify({"status": "failed", "message": "URL tidak valid"}), 400
    
    if not validate_year(data['year']):
        return jsonify({"status": "failed", "message": "Format tahun tidak valid"}), 400
    
    if not data["text_scraped"]:
        return jsonify({"status": "failed", "message": "Lakukan scraping terlebih dahulu"}), 400
    
    
    try:
        new_id = str(uuid.uuid4())
        new_dataset = UrlDatasets(
            id=new_id,
            title=data['title'], 
            url=data['link'], 
            year=data['year'], 
            extracted_text=data['text_scraped'], 
            created_at=datetime.now(), 
            updated_at=datetime.now(),
            created_by_id=session['user_id']
        )

        new_history = ModifiedDataset(
            file_id=new_id,
            file_type=FileType.url,
            action=Action.add,
            modified_by_id=session['user_id'],
            created_at=datetime.now()
        )

        db.session.add(new_dataset)
        db.session.add(new_history)
        db.session.commit()

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.url) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_url = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_url_list = [data.to_dict() for data in not_updated_url]

        return jsonify({"status": "success", "message": "Data berhasil disimpan", "data": new_dataset.to_dict(), "not_updated_url": not_updated_url_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat menyimpan data"}), 500

@jwt_required
@role_required('admin')
@link_controller.route('/link/<id>', methods=['PATCH'])
def update_link_dataset(id):
    data = request.get_json()
    print("\n", data)

    # 1. Cek JSON kosong?
    if not data:
        return jsonify({"status": "failed", "message": "Data yang dikirimkan tidak boleh kosong"}), 400
    
    # 2. Cek setiap key ada
    if ("title" not in data) or ("link" not in data) or ("year" not in data) or ("extracted_text" not in data):
        return jsonify("Format data yang dikirimkan tidak sesuai"), 400
    
    if not data["title"] or not data["link"] or not data["year"]:
        return jsonify({"status": "failed", "message": "Data tidak boleh kosong"}), 400

    if not validate_title(data['title']):
        return jsonify({"status": "failed", "message": "Judul tidak boleh menggunakan karakter simbol"}), 400
    
    if len(data['title']) < 5 or len(data['title']) > 100:
        return jsonify({"status": "failed", "message": "Judul harus mengandung 5-20 karakter"}), 400
    
    if not data["link"]:
        return jsonify({"status": "failed", "message": "Link/url tidak boleh kosong"}), 400
    
    if not data["year"]:
        return jsonify({"status": "failed", "message": "Tahun tidak boleh kosong"}), 400
    
    if not validate_link(data['link']):
        return jsonify({"status": "failed", "message": "URL tidak valid"}), 400
    
    if not validate_year(data['year']):
        return jsonify({"status": "failed", "message": "Format tahun tidak valid"}), 400
    
    if not data["extracted_text"]:
        return jsonify({"status": "failed", "message": "Lakukan scraping terlebih dahulu"}), 400
    
    try:
        dataset = UrlDatasets.query.filter_by(id=id).first()
        print("Isi dataset: ", dataset)
        if not dataset:
            return jsonify({"status": "failed", "message": "Data tidak ditemukan"}), 404
        
        dataset.title = data['title']
        dataset.url = data['link']
        dataset.year = data['year']
        dataset.extracted_text = data['extracted_text']
        dataset.updated_at = datetime.now()

        new_history = ModifiedDataset(
            file_id=id,
            file_type=FileType.url,
            action=Action.update,
            modified_by_id=session['user_id'],
            created_at=datetime.now()
        )

        db.session.add(new_history)
        db.session.commit()

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.url) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_url = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_url_list = [data.to_dict() for data in not_updated_url]

        print("Isi dataset: ", dataset.to_dict())

        return jsonify({"status": "success", "message": "Data berhasil diperbarui", "data_updated": dataset.to_dict(), "not_updated_url": not_updated_url_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat memperbarui data"}), 500

@link_controller.route('/link/<id>', methods=['DELETE'])
def delete_link_dataset(id):
    try:
        dataset = UrlDatasets.query.filter_by(id=id).first()
        if not dataset:
            return jsonify({"status": "failed", "message": "Data tidak ditemukan"}), 404
        
        dataset.deleted_at = datetime.now()

        new_history = ModifiedDataset(
            file_id=id,
            file_type=FileType.url,
            action=Action.delete,
            modified_by_id=session['user_id'],
            created_at=datetime.now()
        )

        db.session.add(new_history)
        db.session.commit()

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.url) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_url = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_url_list = [data.to_dict() for data in not_updated_url]

        return jsonify({"status": "success", "message": "Data berhasil dihapus", "not_updated_url": not_updated_url_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat menghapus data"}), 500
    

    