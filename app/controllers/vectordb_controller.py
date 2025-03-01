from flask import Blueprint, request, jsonify, session
from ..models import PdfDatasets, UrlDatasets, EmbedderSetting, Chunks, ModifiedDataset, db
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from tools.indexing import create_db_with_langchain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from ..utils.get_overlap import find_overlap
import math
import asyncio
import os
from datetime import datetime
from flask_jwt_extended import jwt_required
from ..utils.authorization import role_required

load_dotenv()
vectordb_controller = Blueprint('vectordb', __name__)

@jwt_required()
@role_required('admin')
@vectordb_controller.route('/<page>', methods=['GET'])
def get_chunks(page):
    page = int(page)
    items_per_page = 5
    first_row = (page - 1) * items_per_page
    last_row = first_row + items_per_page

    print("")

    if page < 1:
        return jsonify({"message": "nomor page tidak boleh kurang dari 1"}), 400
    
    try:
        record_modified_dataset = ModifiedDataset.query.filter(ModifiedDataset.action.isnot(None)).first()

        if not record_modified_dataset:
            this_is_latest_db = True
        else:
            this_is_latest_db = False

        # Ambil History pengaturan yang terbaru
        latest_embedder_setting = EmbedderSetting.query.order_by(EmbedderSetting.created_at.desc()).first()
        setting = latest_embedder_setting.to_dict()
        print(setting["vector_db_name"])
        vector_db_name = setting["vector_db_name"]
        
        embedder = OpenAIEmbeddings(model=setting["embedder"])
        
        vector_db_path = f"src/db/{vector_db_name}"

        if not os.path.exists(vector_db_path):
            return jsonify({"message": "terjadi kesalahan saat mengakses vector db, mohon buat vector db ulang"}), 404

        vector_db = FAISS.load_local(vector_db_path, embedder, allow_dangerous_deserialization=True)
        faiss_index = vector_db.index
        total_chunk = faiss_index.ntotal
        pages = math.ceil(total_chunk / 5)

        all_data = []

        # Batasi last_row agar tidak melebihi total_chunk
        adjusted_last_row = min(last_row, total_chunk)

        for i in range(first_row, adjusted_last_row):
            vector = faiss_index.reconstruct(i)
            doc = vector_db.docstore.search(vector_db.index_to_docstore_id[i])

            overlap = None
            
            if i > 0 and i < total_chunk - 1 :
                prev_doc = vector_db.docstore.search(vector_db.index_to_docstore_id[i-1])
                if doc.metadata["page"] == prev_doc.metadata["page"]:
                    overlap = find_overlap(prev_doc.page_content, doc.page_content)

            all_data.append(
                {
                    "index": i,
                    # "vector": str(vector),
                    "vector": str(vector.tolist()),
                    "chunk": doc.page_content,
                    "metadata": doc.metadata,
                    "overlap": overlap
                }
            )

        return jsonify({"message": "success", "data": all_data, "setting": setting, "total_chunk": total_chunk, "pages": pages, "current_page": page, "items_per_page": items_per_page, "is_latest_db": this_is_latest_db }), 200
    except Exception as e:
        import traceback
        print("Posisi error:", str(e))
        print(traceback.format_exc())  # Menampilkan stack trace lengkap
        return jsonify({"message": "Gagal saat memuat vector db dengan FAISS", "data": None}), 500


@jwt_required()
@role_required('admin')
@vectordb_controller.route('/generate', methods=['POST'])
async def generate_vector_db():
    # Ambil JSON
    data_json = request.get_json()

    key_json = ['chunk_size', 'chunk_overlap', 'embedder']
    embedder_list = ['text-embedding-ada-002', 'text-embedding-3-small', 'text-embedding-3-large']

    for key in key_json:
        if key not in data_json:
            return jsonify({"status": "failed", "message": f"{key.replace('_', ' ')} tidak ditemukan"}), 400
        if not data_json.get(key):
            return jsonify({"status": "failed", "message": f"{key.replace('_', ' ')} tidak boleh kosong"}), 400
        if key == 'chunk_size':
            try:
                chunk_size = int(data_json['chunk_size'])
                if chunk_size <= 100:
                    return jsonify({"status": "failed", "message": "Chunk size harus lebih besar dari 100"}), 400
            except ValueError as e:
                print(e)
                return jsonify({"status": "failed", "message": "Chunk size harus berupa angka"}), 400
            
        if  key == 'chunk_overlap':
            try:
                chunk_overlap = int(data_json['chunk_overlap'])
                if chunk_overlap <= 100:
                    return jsonify({"status": "failed", "message": "Chunk overlap harus lebih besar dari 100"}), 400
            except ValueError as e:
                print(e)
                return jsonify({"status": "failed", "message": "Chunk overlap harus berupa angka"}), 400
            
        if key == 'embedder':
            if data_json[key] not in embedder_list:
                return jsonify({"status": "failed", "message": "Embedder tidak valid"}), 400
            
    chunk_size = int(data_json['chunk_size'])
    chunk_overlap = int(data_json['chunk_overlap'])
    embedder = data_json['embedder']

    if  chunk_size < chunk_overlap:
        return jsonify({"status": "failed", "message": "Chunk size harus lebih besar dari chunk overlap"}), 400
    
    # Ambil data PDF dan URL dari database
    data_pdf = PdfDatasets.query.with_entities(PdfDatasets.filename, PdfDatasets.description, PdfDatasets.year).filter(PdfDatasets.deleted_at.is_(None)).all()
    print("Data PDF berhasil diambil dari database")
    data_url = UrlDatasets.query.with_entities(UrlDatasets.url, UrlDatasets.title, UrlDatasets.year, UrlDatasets.extracted_text).filter(UrlDatasets.deleted_at.is_(None)).all()
    print("Data URL berhasil diambil dari database")

    # Inisiasi loader untuk mengekstrak file PDF di folder dataset
    loader = PyPDFDirectoryLoader(path="dataset")

    # Ekstrak dataset PDF ke dalam list Document
    documents = await asyncio.to_thread(loader.load) 

    # Ubah data dari database ke bentuk dict dengan nama file sebagai key nya
    # Tujuannya untuk membandingkan dengan file pdf yang ada di folder dataset apakah sudah ada atau tidak
    pdf_dict = {
        data.filename: {
            "description": data.description,
            "year": data.year
        }
        for data in data_pdf
    }

    # Buat Variabel kosong untuk menyimpan data ke FAISS
    full_docs = []

    for doc in documents:
        # Ambil nama file dari filepath nya
        filename = doc.metadata['source'].split("\\")[-1] 

        # Jika file di folder tidak terdaftar di database maka skip ke iterasi selanjutnya
        if filename not in pdf_dict:
            continue

        metadata = pdf_dict[filename]

        # Tambahkan metadata tahun dan sumber data
        doc.metadata['tahun'] = metadata['year']
        doc.metadata['sumber data'] = metadata['description']

        full_docs.append(
            Document(
                page_content=doc.page_content,
                metadata=doc.metadata
            )
        )

    for data in data_url:
        full_docs.append(
            Document(
                page_content=data.extracted_text,
                metadata={
                    "tahun": data.year,
                    "sumber data": data.url,
                    "page": None
                }
            )
        )

    response = create_db_with_langchain(
        docs=full_docs, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        embedding_model=embedder,
        )

    if response['status'] == 'success':
        try:
            new_setting = EmbedderSetting(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap, 
                embedder=embedder, 
                vector_db_name=response['db_name'],
                created_user_id=session['user_id'],
                created_at=datetime.now()
            )
            db.session.add(new_setting)
            db.session.query(ModifiedDataset).update({ModifiedDataset.action: None})
            db.session.commit()
            return jsonify({'message': "Basis data vektor berhasil dibuat", "setting": new_setting.to_dict(), "data": response['data'], "total_chunk": response['total_chunk'], "is_latest_db": True}), 200
        except Exception as e: 
            print("Posisi error: ", e)
            return jsonify({'message': "Gagal menyimpan data ke database"}), 500
        
    return jsonify({'message': "Basis data vektor gagal dibuat, terdapat kesalahan internal"}), 500
