import re
from src.state import AgentState
from src.prompt import CONTEXT_ABBREVIATIONS

def build_regex_pattern(abbreviations):
    # Escape semua kunci untuk memastikan karakter khusus tidak menyebabkan error di regex
    escaped_keys = [key for key in abbreviations.keys()]
    
    # Gabungkan kunci dengan OR (|)
    pattern = '|'.join(escaped_keys)
    
    # Buat regex pattern dengan pembatas kata (\b) dan ignore case
    return re.compile(r'\b(' + pattern + r')\b', re.IGNORECASE)


def expand_abbreviations(question, abbreviations):
    # Buat regex pattern untuk mencocokkan akronim
    pattern = build_regex_pattern(abbreviations)
    
    # Fungsi untuk mengganti akronim dengan ekspansinya
    def replace_match(match):
        # Ambil akronim yang cocok dan ubah ke uppercase
        matched_acronym = match.group(0).upper()
        
        # Ganti dengan ekspansi dari kamus, jika tersedia
        return abbreviations.get(matched_acronym, matched_acronym)
    
    # Gunakan regex untuk mengganti semua akronim yang cocok
    return pattern.sub(replace_match, question)

print(expand_abbreviations("apa krs itu", CONTEXT_ABBREVIATIONS))