import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_openai = init_chat_model(model="gpt-6-luna", api_key=OPENAI_API_KEY, use_responses_api=True, output_version="responses/v1",)
#print(llm_openai)