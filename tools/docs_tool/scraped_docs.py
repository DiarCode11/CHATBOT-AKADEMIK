import pdfplumber
import re
import pandas as pd
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_other_info(doc_list: list):
    # dataframe
    docs_list = []

    # Faculty list
    fac_list = ["FBS", "FE", "FHIS", "FIP", "FK", "FMIPA", "FOK", "FTK", "Pascasarjana"]

    for doc in doc_list:
        try:
            # Membaca teks dari semua halaman
            with pdfplumber.open(f"data/{doc[0]}.pdf") as pdf:
                # Variabel untuk menyimpan teks gabungan
                full_text = ""

                for page in pdf.pages:
                    # Tambahkan teks dari setiap halaman ke variabel full_text
                    full_text += page.extract_text() + " "

                print("Ekstraksi file: ", doc[0])

                if doc[0] in fac_list:
                    full_text = re.sub(r'(?<=\n)(Visi Fakultas|Pimpinan|Daftar Jurusan|Info Kontak Fakultas)', r'\n\n\n\1', full_text)
                    print(doc[0] +" berhasil diregex")

            docs = Document(page_content=full_text, metadata={"file_path": f"data/{doc[0]}.pdf", "description": doc[1], "year": doc[2]})
            docs_list.append(docs)

        except Exception as e:
            print(e)
            break
            

    print(docs_list)
    return docs_list

def split_docs(docs: Document):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False
    )

    splitted_docs = text_splitter.split_documents(docs)

    df = pd.DataFrame([
        {
            "content": doc.page_content,
            **(doc.metadata or {})  # Gunakan {} jika metadata kosong
        }
        for doc in splitted_docs
    ])

    df.to_excel("data_excel/other_docs_chunk.xlsx", index=False)

    return df


    

if __name__ == "__main__":
    docs_list = [
        ["FAQ DOSEN", "FAQ UMUM - UPA TIK Undiksha", 2024],
        ["FAQ MAHASISWA", "FAQ UMUM - UPA TIK Undiksha", 2024],
        ["FAQ REMUNERASI", "FAQ UMUM - UPA TIK Undiksha", 2024],
        ["FAQ UMUM", "FAQ UMUM - UPA TIK Undiksha", 2024],
        ["FBS", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FE", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FHIS", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FIP", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FK", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FMIPA", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FOK", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["FTK", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["Pascasarjana", "INFORMASI FAKULTAS DI UNDIKSHA", 2024],
        ["Umum", "INFORMASI UMUM UNDIKSHA", 2024],
        ["Sistem Tugas Akhir", "INFORMASI SISTEM TUGAS AKHIR DI UNDIKSHA", 2024],
        ["Panduan-SIAKNG-Students-Exchange", "PANDUAN SIAK UNDIKSHA", 2021],
    ]
    
    docs = extract_other_info(docs_list)
    split_docs(docs)
    