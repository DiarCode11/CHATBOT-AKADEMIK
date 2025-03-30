import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os 

def generate_excel(embedder: OpenAIEmbeddings, db_path: str, filename: str = "new_dataset.xlsx"):
    vector_db = FAISS.load_local(db_path, embedder, allow_dangerous_deserialization=True)
    faiss_index = vector_db.index
    total_chunk = faiss_index.ntotal

    data = []

    for i in range(0, total_chunk):
        vector = faiss_index.reconstruct(i)
        doc = vector_db.docstore.search(vector_db.index_to_docstore_id[i])
        row = [i + 1, doc, vector]
        data.append(row)
    
    df = pd.DataFrame(data, columns=['No', 'Chunk', 'Vector'])

    if not os.path.exists("output_excel"):
        os.makedirs("output_excel")

    # Simpan DataFrame ke file Excel
    df.to_excel(f"output_excel/{filename}", index=False, engine="openpyxl")

    print(f"File Excel berhasil dibuat: {filename}")
    



# embedder =OpenAIEmbeddings(model="text-embedding-3-small")

# conf = {
#     "db_path": "src/db/db_20250314_092647",
#     "embedder": embedder
# }

# generate_excel(**conf)
            