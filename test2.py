import camelot

# Membaca file PDF dan mengekstrak tabel di halaman pertama
tables = camelot.read_pdf("data/Pedoman-Studi-2017.pdf", pages="1")

# Menampilkan jumlah tabel yang berhasil diekstrak
print(f"Jumlah tabel yang ditemukan: {len(tables)}")

# Menampilkan tabel pertama yang diekstrak
print(tables[0].df)  # DataFrame dari tabel pertama
