import pdfplumber
import re
import pandas as pd
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_academic_guidelines(pdf_path="data/Fix Kalender-Akademik-Tahun-Ajaran-2024-2025 scan (2).pdf"):
    # Variabel untuk menyimpan teks gabungan
    full_text = ""

    # Membaca teks dari semua halaman
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Tambahkan teks dari setiap halaman ke variabel full_text
            full_text += page.extract_text() + " "

    # Menghapus footer dengan regex
    cleaned_text = re.sub(r"Kalender Akademik Universitas Pendidikan Ganesha 2024/2025_+\s\d+", "", full_text)

    updated_text = re.sub(r"([A-G]\.)", r'\n\n\1', cleaned_text)

    print(updated_text)

    return [Document(page_content=updated_text, metadata={"file_path": pdf_path, "description": "Kalender Akademik Universitas Pendidikan Ganesha Tahun Ajaran 2024/2025", "year": 2024})]

def split_docs(docs: Document):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=1000,
        chunk_overlap=200
    )

    splitted_docs = text_splitter.split_documents(docs)

    df = pd.DataFrame([
        {
            "content": doc.page_content,
            **(doc.metadata or {})  # Gunakan {} jika metadata kosong
        }
        for doc in splitted_docs
    ])

    df.to_excel("data_excel/academic_calendar_chunk.xlsx", index=False)

    return df

if __name__ == "__main__":
    docs =extract_academic_guidelines()
    splitted_docs = split_docs(docs)
    print(splitted_docs)
    