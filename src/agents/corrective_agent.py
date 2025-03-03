from src.state import AgentState
from src.prompt import CORRECTIVE_PROMPT
from tools.generator import chat_openai

class CorrectiveAgent:
    @staticmethod
    def correct(state: AgentState) -> str:
        expanded_question = state['expanded_question']
        prompt = CORRECTIVE_PROMPT.format(question=expanded_question, data=state['raw_context'])
        state['corrective_prompt'] = prompt
        llm_model = state['llm_model']

        try:
            response = chat_openai(prompt, model=llm_model)
            state['cleaned_context'] = response
            print(response)
            print("--  CORRECTIVE AGENT --\n\n")
            return state
        except Exception as e:
            print("Posisi Kode Error: Corrective Agent")
            print("Error: ", str(e))
            raise
        