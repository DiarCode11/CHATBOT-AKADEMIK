from src.state import AgentState
from tools.generator import chat_openai

class Generator:
    @staticmethod
    def generate(state: AgentState) -> str:
        question = state['question']
        relevant_response = state['cleaned_context']
        llm_model = state['llm_model']

        GENERATOR_PROMPT = f"""
        Namamu adalah AKASHA yaitu chatbot untuk informasi akademik Universitas Pendidikan Ganesha (Undiksha) yang hebat dalam memberikan informasi, ikuti aturan berikut. 
        - Namamu AKASHA terinspirasi dari kependekan dari Akademik Undiksha 
        - Berikan jawaban hanya yang bersumber dari data yang diberikan
        - Jika ada dua data yang sama, gunakan data terbaru (dapat dilihat di metadata "tahun")
        - gunakan bahasa yang informatif dan sopan
        - Sesuaikan jawaban jika pertanyaan menggunakan bahasa selain bahasa indonesia
        - Jawaban hanya berpatokan pada data yang diberikan, jangan gunakan pengetahuanmu sendiri.
        - Kamu harus mengatakan tidak tau jika data yang diberikan tidak ada
        - setiap akhir paragraf tambahkan sitasi ke sumber dokumen dalam square bracket, contohnya seperti :
"Machine learning algorithms require large datasets for training. The quality of data directly impacts model performance. [Source: ML_handbook.pdf, chapter 3]
        pertanyaan pengguna: {question}
        Data yang diberikan: {relevant_response}
        """

        try:
            state['expanded_question'] = None
            state['corrective_prompt'] = None
            state['cleaned_context'] = None
            state['generator_prompt'] = GENERATOR_PROMPT
            final_response = chat_openai(GENERATOR_PROMPT, model=llm_model)
            state['final_answer'] = final_response

            print(final_response)
            print("--  GENERATOR AGENT --\n\n")
            return state

        except Exception as e:
            print("Posisi Kode Error: Generator Agent")
            print("Error: ", str(e))
            raise