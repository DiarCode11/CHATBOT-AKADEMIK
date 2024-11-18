from tools.retriever import similiarity_search
from tools.augment import QUESTION_PROMPT
from tools.generator import chat_openai, chat_ollama


def create_response(question: str):
    # Proses Retriever
    relevant_chunks = similiarity_search(question)

    # Proses Augmentasi
    complete_prompt = QUESTION_PROMPT.format(question=question, data=relevant_chunks)

    # Proses Generation
    response_llm = chat_openai(question=complete_prompt, model="gpt-4o-mini")
    # response_llm = chat_ollama(question=complete_prompt)

    print(response_llm)

    return response_llm


if __name__ == "__main__":
    question = "siapa saja dosen yang ada di jurusan teknik informatika"
    create_response(question)