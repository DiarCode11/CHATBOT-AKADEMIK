from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SparseRetriever:
    def __init__(self, documents):
        """
        Inisialisasi sparse retriever dengan dokumen yang tersedia
        
        Args:
            documents (list): Daftar dokumen teks
        """
        self.documents = documents
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
    
    def retrieve(self, query, top_k=3):
        """
        Mencari dokumen yang relevan berdasarkan query
        
        Args:
            query (str): Query pencarian
            top_k (int): Jumlah dokumen teratas yang dikembalikan
        
        Returns:
            list: Dokumen yang paling relevan
        """
        query_vector = self.vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Urutkan dokumen berdasarkan similaritas
        similar_indices = cosine_similarities.argsort()[::-1][:top_k]
        
        return [self.documents[idx] for idx in similar_indices]

# Contoh penggunaan
documents = [
    "Python adalah bahasa pemrograman populer",
    "Machine learning menggunakan algoritma kompleks",
    "Natural language processing membutuhkan data besar machine learning",
    "Kecerdasan buatan berkembang pesat"
]

retriever = SparseRetriever(documents)
query = "apa itu python"
results = retriever.retrieve(query)

print("Hasil Retrieval:")
for doc in results:
    print("- " + doc)