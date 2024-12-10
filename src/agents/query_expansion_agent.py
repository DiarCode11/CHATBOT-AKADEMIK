import re
from src.state import AgentState
from src.prompt import CONTEXT_ABBREVIATIONS

def build_regex_pattern(abbreviations):
    """
    Membangun pola regex untuk mencocokkan akronim dalam teks.
    
    Args:
        abbreviations (dict): Kamus yang berisi pasangan {akronim: ekspansi}.
        
    Returns:
        re.Pattern: Pola regex yang dapat mencocokkan akronim dari kamus.
    
    Proses:
        - Escape semua karakter khusus dalam kunci kamus menggunakan `re.escape`.
        - Gabungkan kunci yang sudah di-escape dengan operator `|` (OR).
        - Tambahkan pembatas kata `\b` untuk memastikan pencocokan akronim sebagai kata utuh.
        - Gunakan `re.IGNORECASE` untuk membuat pencocokan tidak peka huruf besar/kecil.
    """
    # Escape semua kunci untuk memastikan karakter khusus tidak menyebabkan error di regex
    escaped_keys = [re.escape(key) for key in abbreviations.keys()]
    
    # Gabungkan kunci dengan OR (|)
    pattern = '|'.join(escaped_keys)
    
    # Buat regex pattern dengan pembatas kata (\b) dan ignore case
    return re.compile(r'\b(' + pattern + r')\b', re.IGNORECASE)


def expand_abbreviations(question, abbreviations):
    """
    Memperluas akronim dalam teks menjadi bentuk lengkapnya berdasarkan kamus.
    
    Args:
        question (str): Teks yang berisi akronim.
        abbreviations (dict): Kamus yang berisi pasangan {akronim: ekspansi}.
        
    Returns:
        str: Teks dengan akronim yang telah diperluas.
    
    Proses:
        - Bangun pola regex untuk mencocokkan akronim menggunakan `build_regex_pattern`.
        - Gunakan `re.sub` untuk mengganti akronim yang cocok dengan bentuk lengkapnya.
        - Setiap kali ada kecocokan, fungsi `replace_match` akan dipanggil.
        - Dalam `replace_match`:
            - Ambil akronim yang cocok dan ubah ke huruf besar (`.upper()`).
            - Ganti dengan ekspansi dari kamus jika tersedia.
            - Jika tidak ditemukan di kamus, kembalikan teks asli.
    """
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


class QueryExpansionAgent:
    @staticmethod
    def expand_query(state: AgentState) -> str:
        question = state['question']

        expanded_question = expand_abbreviations(question, CONTEXT_ABBREVIATIONS)

        state['expanded_question'] = expanded_question

        print("Original question: ", question)
        print("Expanded question: ", expanded_question)


        print("--  QUERY EXPANSION AGENT --\n\n")

        return state




