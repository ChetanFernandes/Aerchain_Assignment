### Not using this. Directlt wiring streamlit ### 

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dataclasses import dataclass
from src.backend.buyer_agent import main

@dataclass
class Data(BaseModel):
    question:str

app = FastAPI(title = "Buyer Analysis Agent")

@app.get("/")
def app_check():
     return {"message": "Welcome to Aerchain Procurement AI"}


@app.post("/data")
def get_payload(data:Data):
     try:
        question = data.question
        response = main(question)
        return response
     except Exception as e:
         return str(e)


# streamlit code

BASE_URL = "http://localhost:8000"

def send_payload(question):
    try:
        payload = {
            "question": question
        }

        response = requests.post(f"{BASE_URL}/data", json=payload)

        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }