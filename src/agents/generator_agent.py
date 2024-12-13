from src.state import AgentState
from tools.generator import chat_openai

class GeneratorAgent:
    @staticmethod
    def generate(state: AgentState) -> str:
        question = state['expanded_question']
        relevant_response = state['cleaned_context']

        GENERATOR_PROMPT = f"""
            Namamu adalah AKASHA yaitu chatbot untuk informasi akademik Universitas Pendidikan Ganesha (Undiksha) yang hebat dalam memberikan informasi, ikuti aturan berikut. 
            - Namamu AKASHA terinspirasi dari kependekan dari Akademik Undiksha 
            - Gunakan bahasa gaul yang mudah dimengerti 
            - Sesuaikan jawaban jika pertanyaan menggunakan bahasa selain bahasa indonesia
            - Jawaban hanya berpatokan pada data yang diberikan, jangan gunakan pengetahuanmu sendiri.
            - Kamu boleh mengatakan tidak tau jika data yang diberikan tidak ada
            pertanyaan pengguna: {question}
            Data yang diberikan: {relevant_response}
        """

        final_response = chat_openai(GENERATOR_PROMPT, model="gpt-4o-mini")

        print(final_response)

        print("--  GENERATOR AGENT --\n\n")

        return {"final_answer": final_response}