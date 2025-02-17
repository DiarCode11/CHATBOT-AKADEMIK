from flask import Blueprint, request, jsonify, session
from ..models import PdfDatasets, UrlDatasets, EmbedderSetting, Chunks, db
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from tools.indexing import create_db_with_langchain
import asyncio
from datetime import datetime

vectordb_controller = Blueprint('vectordb', __name__)

@vectordb_controller.route('/', methods=['GET'])
def get_chunks():
    chunks = Chunks.query.filter(Chunks.deleted_at.is_(None)).all()
    print(chunks)


@vectordb_controller.route('/generate', methods=['POST'])
async def generate_vector_db():
    # Ambil JSON
    data_json = request.get_json()

    # Simpan isi JSON 
    chunk_size = data_json['chunk_size']
    chunk_overlap = data_json['chunk_overlap']
    embedder = data_json['embedder']

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

    full_chunks_db = []

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
                    "sumber data": data.url
                }
            )
        )

    response = create_db_with_langchain(docs=full_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap, embedding_model=embedder)

    if response['status'] == 'success':
        try:
            new_setting = EmbedderSetting(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap, 
                embedder=embedder, 
                created_user_id='53c3b91f-3946-4e63-be22-663f331a0b77', 
                created_at=datetime.now(), 
                updated_at=datetime.now()
            )
            db.session.add(new_setting)
            db.session.commit()
            return jsonify({'response': "Basis data vektor berhasil dibuat"}), 200
        except Exception as e: 
            print("Posisi error: ", e)
            return jsonify({'response': "Gagal menyimpan data ke database"}), 500
        
    return jsonify({'response': "Basis data vektor gagal dibuat, terdapat kesalahan internal"}), 500
