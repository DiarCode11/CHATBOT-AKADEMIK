from src.state import AgentState

class GeneratorAgent:
    @staticmethod
    def generate(state: AgentState) -> str:
        response = state['cleaned_context']

        

        print("--  GENERATOR AGENT --\n\n")

        return response