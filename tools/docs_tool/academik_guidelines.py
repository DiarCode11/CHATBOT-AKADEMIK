import pdfplumber
import re
import pandas as pd
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_academic_guidelines(pdf_path="data/Pedoman-Studi-2017.pdf"):
    # Variabel untuk menyimpan teks gabungan
    full_text = ""

    # Membaca teks dari semua halaman
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Tambahkan teks dari setiap halaman ke variabel full_text
            full_text += page.extract_text() + " "

    # Menghapus footer dengan regex
    
    patterns = [
        [r"Pedoman Studi Universitas Pendidikan Ganesha Tahun 2017 \d{1,3}", ""],
        [r'(\d+\.\sProgram Studi.*?)', r'\n\n\1'],
        [r"(^|\n)([IVXLCDM]+\.\s.*)", r"\1\n\n\2"],
    ]

    for pattern in patterns:
        full_text = re.sub(pattern[0], pattern[1], full_text)


    # cleaned_text = re.sub(r"Pedoman Studi Universitas Pendidikan Ganesha Tahun 2017 \d{1,3}", "", full_text)

    # # Menambahkan "\n\n" sebelum nama program studi
    # updated_text = re.sub(r'(\d+\.\sProgram Studi.*?)', r'\n\n\1', cleaned_text)

    return [Document(page_content=full_text, metadata={"file_path": pdf_path, "description": "Pedoman Studi Universitas Pendidikan Ganesha Tahun 2017", "year": 2017})]

def split_docs(docs: Document, chunk_size=2000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n\n"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    splitted_docs = text_splitter.split_documents(docs)

    df = pd.DataFrame([
        {
            "content": doc.page_content,
            **(doc.metadata or {})  # Gunakan {} jika metadata kosong
        }
        for doc in splitted_docs
    ])

    df.to_excel("data_excel/academic_guidelines_chunk.xlsx", index=False)

    return df

if __name__ == "__main__":
    docs = extract_academic_guidelines()
    splitted_docs = split_docs(docs)
    print(splitted_docs)
    