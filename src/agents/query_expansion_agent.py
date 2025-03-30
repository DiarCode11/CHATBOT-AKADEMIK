import re
from src.state import AgentState
from src.prompt import CONTEXT_ABBREVIATIONS

def build_regex_pattern(abbreviations):
    # Gabungkan semua akronim dengan OR (|)
    pattern = '|'.join(abbreviations.keys())
    
    # Buat regex pattern dengan batasan kata (\b) dan ignore case
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
    





