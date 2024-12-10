from src.state import AgentState
from src.prompt import CORRECTIVE_PROMPT
from tools.generator import chat_openai

class CorrectiveAgent:
    @staticmethod
    def correct(state: AgentState) -> str:
        expanded_question = state['expanded_question']

        prompt = CORRECTIVE_PROMPT.format(question=expanded_question, data=state['raw_context'])

        response = chat_openai(prompt, model="gpt-4o-mini")

        state['cleaned_context'] = response

        print(response)

        print("--  CORRECTIVE AGENT --\n\n")
        