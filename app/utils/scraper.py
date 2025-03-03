import requests
import re
from bs4 import BeautifulSoup

def clean_text(text: str):
    # Hapus newline di awal dan akhir teks
    text = text.strip()

    # Ganti lebih dari dua newline berturut-turut menjadi hanya dua newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

def remove_non_ascii(text):
    """Menghapus semua karakter non-ASCII dari teks."""
    return ''.join(char for char in text if ord(char) < 128)

# Mengambil konten HTML dari halaman
def scrape(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            main_tag = soup.find("main")  # Mengambil elemen <main>
            if main_tag:
                print("Hasil scraping berhasil disimpan ke file index.html")
                result = str(main_tag.get_text())

                # Clean result
                clean_result = clean_text(result)

                clean_from_non_ascii = remove_non_ascii(clean_result)

                return {"status": "success", "message": "Scraping berhasil"}, clean_from_non_ascii
            else:
                return {"status": "failed", "message": "Tag <main> tidak ditemukan dalam halaman."}, None
        else:
            print("Gagal mengambil halaman. Status code:", response.status_code)
            return {"status": "failed", "message": "Halaman web tersebut tidak dapat discrap"}, None
    except Exception as e:
        print("Terjadi kesalahan saat mengambil halaman:", str(e))
        return {"status": "failed", "message": "Halaman web tersebut tidak dapat discrap"}, None
    


# if __name__ == "__main__":
#     url = "https://fe.undiksha.ac.id/profil/sejarah-singkat/"
#     response, data = scrape(url)
#     print(response, data)