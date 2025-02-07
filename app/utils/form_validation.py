import re

TITLE_REGEX = r"^[a-zA-Z0-9 ]+$"  # Hanya boleh huruf dan angka
LINK_REGEX = r"^https?:\/\/[^\s/$.?#].[^\s]*$"  # URL harus diawali dengan http:// atau https://
YEAR_REGEX = r"^(19|20)\d{2}$"  # Tahun harus 4 digit, mulai dari 1900-2099

def validate_title(title: str):
    return bool(re.match(TITLE_REGEX, title))

def validate_link(link: str):
    return bool(re.match(LINK_REGEX, link))

def validate_year(year: str):
    return bool(re.match(YEAR_REGEX, year))

if __name__ == "__main__":
    print(validate_title("contoh judul"))