from src.state import AgentState
from tools.generator import chat_openai

class GeneratorAgent:
    @staticmethod
    def generate(state: AgentState) -> str:
        question = state['expanded_question']
        relevant_response = state['cleaned_context']
        llm_model = state['llm_model']

        GENERATOR_PROMPT = f"""
            Namamu adalah AKASHA yaitu chatbot untuk informasi akademik Universitas Pendidikan Ganesha (Undiksha) yang hebat dalam memberikan informasi, ikuti aturan berikut. 
            - Namamu AKASHA terinspirasi dari kependekan dari Akademik Undiksha 
            - gunakan bahasa yang informatif dan sopan
            - Sesuaikan jawaban jika pertanyaan menggunakan bahasa selain bahasa indonesia
            - Jawaban hanya berpatokan pada data yang diberikan, jangan gunakan pengetahuanmu sendiri.
            - Kamu harus mengatakan tidak tau jika data yang diberikan tidak ada
            - Jika informasi ditemukan, tampilkan sumber dari data tersebut dalam bentuk footer dengan format 'Sumber data: <nama-nama sumber dokumen atau link, pisahkan dengan koma>', dapat dilihat pada metadata "sumber data"
            - Untuk footer jangan ubah menjadi markdown link, cukup mardown bold saja
            - Jika informasi tidak ditemukan, maka jangan membuat footer
            pertanyaan pengguna: {question}
            Data yang diberikan: {relevant_response}
        """

        try:
            final_response = chat_openai(GENERATOR_PROMPT, model=llm_model)
            print(final_response)
            print("--  GENERATOR AGENT --\n\n")
            return {"final_answer": final_response}

        except Exception as e:
            print("Posisi Kode Error: Generator Agent")
            print("Error: ", str(e))
            raise