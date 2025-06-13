from flask import Blueprint, request, jsonify, session, make_response
from ..models import PdfDatasets, ModifiedDataset, FileType, db, Action
from tools.api_tools import validate_file, validate_json
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, set_access_cookies, unset_jwt_cookies
from datetime import datetime
from ..utils.authorization import role_required
from sqlalchemy import func
import os
import dotenv
import uuid

pdf_controller = Blueprint('pdf', __name__)

# Endpoint untuk menampilkan semua dataset
@pdf_controller.route('/pdf', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_pdf_dataset():
    datasets = PdfDatasets.query.filter(PdfDatasets.deleted_at.is_(None)).order_by(PdfDatasets.created_at.desc()).all()

    # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
    subquery = db.session.query(
        ModifiedDataset.file_id,
        func.max(ModifiedDataset.created_at).label("max_created_at")
    ).filter(
        (ModifiedDataset.file_type == FileType.pdf) & (ModifiedDataset.action != None)
    ).group_by(ModifiedDataset.file_id).subquery()

    # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
    not_updated_pdf = ModifiedDataset.query.join(
        subquery,
        (ModifiedDataset.file_id == subquery.c.file_id) &
        (ModifiedDataset.created_at == subquery.c.max_created_at)
    ).order_by(ModifiedDataset.created_at.desc()).all()

    print("Isi dataset: ", datasets)
    result = [
        {
            "id": data.id,
            "filename": data.filename,
            "description": data.description,
            "year": data.year,
            "created_by_id": data.created_by_id,
            "created_at": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": data.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for data in datasets
    ]

    not_updated_pdf_list = [data.to_dict() for data in not_updated_pdf]

    return jsonify({"status": "success", "data": result, "not_updated_pdf": not_updated_pdf_list}), 200

# Endpoint untuk menambahkan dataset
@jwt_required()
@role_required('admin')
@pdf_controller.route('/pdf', methods=['POST'])
def add_pdf_dataset():
    year = request.form.get('year')

    url = os.getenv("DOMAIN")

    if not (year.isdigit() and len(year) == 4):
        return jsonify({"status": "failed", "message": "Format tahun tidak valid"}), 400

    file = request.files.get('file')

    if not file:
      return jsonify({"status": "failed", "message": "Parameter file tidak ditemukan"}), 400

    filename = secure_filename(file.filename)
    print("Nama file yang dikirim: ", filename)

    # Ambil JSON dari form-data
    data = {
        "file": filename,
        "filetype": request.form.get('filetype'),
        "year": request.form.get('year'),
        "description": request.form.get('description')
    }

     # Validasi apakah data JSON lengkap
    json_error, null_keys = validate_json(data, ['file', 'year'])
    if json_error:
        print("Isi error json: ", json_error)
        return jsonify({"status": "failed", "message": json_error, "null_keys": null_keys}), 400

    # Validasi file
    file_error = validate_file(file)
    if file_error:
        return jsonify({"status": "failed", "message": file_error}), 400

    # Buat ID untuk dokumen baru
    new_id = str(uuid.uuid4())

    # Jika Validasi telah selesai
    new_pdf = PdfDatasets(
        id=new_id,
        filename=filename,
        year=data['year'],
        url=f"{url}/view/{filename}",
        description=data['description'],
        created_by_id=session['user_id'],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Simpan history 
    new_history = ModifiedDataset(
        file_id=new_id,
        file_type=FileType.pdf,
        action=Action.add,
        modified_by_id=session['user_id'],
        created_at=
        datetime.now()
    )

    # Simpan ke database
    try:
        if not os.path.exists("dataset"):
            os.makedirs("dataset")

        # Simpan file ke folder
        file.save(os.path.join("dataset", filename))

        # Simpan data ke database
        db.session.add(new_pdf)
        db.session.add(new_history)
        db.session.commit()

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.pdf) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_pdf = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_pdf_list = [data.to_dict() for data in not_updated_pdf]

        return jsonify({"status": "success", "message": "Data berhasil ditambahkan", "data": new_pdf.to_dict(), "not_updated_pdf": not_updated_pdf_list}), 201
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat menyimpan data"}), 500

@jwt_required()
@role_required('admin')
@pdf_controller.route('/pdf/<id>', methods=['PATCH'])
def update_pdf_dataset(id):
    try:
        dataset = PdfDatasets.query.filter_by(id=id).first()
        file = request.files.get('file')

        if not dataset:
            return jsonify({"status": "failed", "message": "Data tidak ditemukan"}), 404

        if not file:
            return jsonify({"status": "failed", "message": "File tidak boleh kosong"}), 400

        filename = secure_filename(file.filename)

        print("\nNama file yang dikirim: ", file.filename)
        print("Nama file di database: ", dataset.filename)

        # Jika ada perubahan pada file
        if filename != dataset.filename:
            if not os.path.exists("dataset"):
                os.makedirs("dataset")

            # Simpan file baru
            file.save(os.path.join("dataset", filename))

            if os.path.exists(os.path.join("dataset", dataset.filename)):
                # Hapus file lama
                os.remove(os.path.join("dataset", dataset.filename))

            # Perbarui nama file di database
            dataset.filename = secure_filename(file.filename)

        # Ambil JSON dari form-data
        data = {
            "file": request.files.get('file'),
            "year": request.form.get('year'),
            "description": request.form.get('description')
        }

        # Validasi apakah data JSON lengkap
        json_error, null_keys = validate_json(data, ['file', 'year'])
        if json_error:
            return jsonify({"status": "failed", "message": json_error, "null_keys": null_keys}), 400

        # Jika Validasi telah selesai
        dataset.year = data['year']
        dataset.description = data['description']
        dataset.updated_at = datetime.now()

        # Simpan history 
        new_history = ModifiedDataset(
            file_id=id,
            file_type=FileType.pdf,
            action=Action.update,
            modified_by_id=session['user_id'],
            created_at=datetime.now()
        )

        db.session.add(new_history)

        # Simpan data ke database
        db.session.commit()

        # Buat subquery untuk mendapatkan nilai maksimum created_at per file_id
        subquery = db.session.query(
            ModifiedDataset.file_id,
            func.max(ModifiedDataset.created_at).label("max_created_at")
        ).filter(
            (ModifiedDataset.file_type == FileType.pdf) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_pdf = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_pdf_list = [data.to_dict() for data in not_updated_pdf]

        return jsonify({"status": "success", "message": "Data berhasil diubah", "data_updated": dataset.to_dict(), "not_updated_pdf": not_updated_pdf_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat mengubah data"}), 500

@jwt_required()
@role_required('admin')
@pdf_controller.route('/pdf/<id>', methods=['DELETE'])
def delete_pdf_dataset(id):
    try:
        dataset = PdfDatasets.query.filter_by(id=id).first()
        if not dataset:
            return jsonify({"status": "failed", "message": "Data tidak ditemukan"}), 404

        # Hapus file
        file_path = os.path.join("dataset", dataset.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Hapus data dari database
        dataset.deleted_at = datetime.now()

        # Simpan history 
        new_history = ModifiedDataset(
            file_id=id,
            file_type=FileType.pdf,
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
            (ModifiedDataset.file_type == FileType.pdf) & (ModifiedDataset.action != None)
        ).group_by(ModifiedDataset.file_id).subquery()

        # Join dengan tabel ModifiedDataset berdasarkan file_id dan created_at yang sama dengan nilai maksimum
        not_updated_pdf = ModifiedDataset.query.join(
            subquery,
            (ModifiedDataset.file_id == subquery.c.file_id) &
            (ModifiedDataset.created_at == subquery.c.max_created_at)
        ).order_by(ModifiedDataset.created_at.desc()).all()

        not_updated_pdf_list = [data.to_dict() for data in not_updated_pdf]
        return jsonify({"status": "success", "message": "Data berhasil dihapus", "not_updated_pdf": not_updated_pdf_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Terjadi kesalahan saat menghapus data"}), 500
