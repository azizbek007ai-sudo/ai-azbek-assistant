import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Gemini API ни созлаймиз (Render'даги環境 ўзгарувчидан олади)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Суҳбат тарихини вақтинча хотирада сақлаб туриш учун рўйхат
chat_history = []

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "AI Azbek assistant is running with memory!"}

@app.post("/chat")
def chat_with_ai(msg: Message):
    # Фойдаланувчи хабарини тарихга қўшамиз
    chat_history.append(f"Фойдаланувчи: {msg.text}")
    
    # Охирги суҳбатларни Gemini тушуниши учун бирлаштирамиз
    prompt = "\n".join(chat_history)
    
    # Gemini моделига сўров юборамиз
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    ai_response = response.text
    # Агентнинг жавобини ҳам тарихга қўшамиз
    chat_history.append(f"Агент: {ai_response}")
    
    return {"response": ai_response}
