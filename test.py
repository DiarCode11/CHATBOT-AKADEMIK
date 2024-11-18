import pdfplumber
import pandas as pd

# Inisialisasi penghitung untuk iterasi nama file
table_count = 1

with pdfplumber.open("data/Pedoman-Studi-2017.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        # Menampilkan dan menyimpan hanya tabel yang tidak kosong
        for table in tables:
            if table:  # Mengecek apakah tabel tidak kosong
                # Menampilkan tabel untuk verifikasi
                print(table)
                print("\n")

                # Mengonversi tabel menjadi DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])

                # Menyimpan DataFrame sebagai file CSV dengan nama berurutan
                filename = f"data_csv/output_{table_count}.csv"
                df.to_csv(filename, index=False)
                print(f"Data berhasil disimpan ke {filename}")

                # Meningkatkan penghitung untuk iterasi berikutnya
                table_count += 1
