from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
import os

# Memuat file .env
load_dotenv()
base_url = os.getenv('OLLAMA_BASE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')


def chat_ollama(question: str, model = 'gemma2'):
    try:
        ollama = OllamaLLM(base_url=base_url, model=model, verbose=True)
        result = ollama.invoke(question)

        return result
    
    except:
        print("Ada masalah di server OLLAMA")

def chat_openai(question: str, model = 'gpt-3.5-turbo-0125'):
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.2
        )

        return completion.choices[0].message.content
    
    except Exception as e:
        print("Ada masalah dengan GPT")
        print("Ini errornya: ", e)

def chat_groq(question: str):
    groq = ChatGroq(
        model="gemma-7b-it",
        max_tokens=None,
        timeout=None,
        temperature=0.1,
    )
    result = groq.invoke(question).content if hasattr(groq.invoke(question), "content") else groq.invoke(question)
    return result



