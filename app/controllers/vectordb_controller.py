from flask import Blueprint, request, jsonify, session, make_response, current_app
from ..models import PdfDatasets, UrlDatasets
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from tools.indexing import create_db_with_langchain
import itertools
import asyncio

vectordb_controller = Blueprint('vectordb', __name__)

@vectordb_controller.route('/generate', methods=['POST'])
async def generate_vector_db():
    data_json = request.get_json()

    chunk_size = data_json['chunk_size']
    chunk_overlap = data_json['chunk_overlap']
    embedder = data_json['embedder']

    print("Isi json: ", chunk_size, chunk_overlap, embedder)

    data_pdf = PdfDatasets.query.with_entities(PdfDatasets.filename, PdfDatasets.description, PdfDatasets.year).filter(PdfDatasets.deleted_at.is_(None)).all()
    print("Data PDF berhasil diambil dari database")
    
    data_url = UrlDatasets.query.with_entities(UrlDatasets.url, UrlDatasets.title, UrlDatasets.year, UrlDatasets.extracted_text).filter(UrlDatasets.deleted_at.is_(None)).all()
    print("Data URL berhasil diambil dari database")

    loader = PyPDFDirectoryLoader(path="dataset")
    documents = await asyncio.to_thread(loader.load) 

    pdf_list = {
        data.filename: {
            "description": data.description,
            "year": data.year
        }
        for data in data_pdf
    }

    url_docs = [
        Document(
            page_content=data.extracted_text,
            metadata={
                "judul": data.title,
                "sumber data": data.url,
                "tahun": data.year
            }
        ) for data in data_url
    ]

    pdf_docs = []

    for doc in documents:
        filename = doc.metadata['source'].split("\\")[-1]
        print(filename)

        if filename not in pdf_list:
            continue

        metadata = pdf_list[filename]

        doc.metadata['tahun'] = metadata['year']
        doc.metadata['sumber data'] = metadata['description']

        pdf_docs.append(
            Document(
                page_content=doc.page_content,
                metadata=doc.metadata
            )
        )

    full_docs = list(itertools.chain(pdf_docs, url_docs))

    response = create_db_with_langchain(docs=full_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap, embedding_model=embedder)

    print(response['chunks'])

    if response['status'] == 'success':
        
        return jsonify({'response': "Basis data vektor berhasil dibuat"}), 200
    return jsonify({'response': "Basis data vektor gagal dibuat, terdapat kesalahan internal"}), 400
