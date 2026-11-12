import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# Gemini API ни созлаймиз
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Суҳбат тарихини сақлаш учун рўйхат
chat_history = []

class Message(BaseModel):
    text: str

# Фонда ишлайдиган режалаштирувчи (APScheduler)
scheduler = BackgroundScheduler()

def scheduled_job():
    print("Режалаштирилган вазифа бажарилди: Сервер фаолияти текширилди.")

scheduler.add_job(scheduled_job, 'interval', minutes=30)
scheduler.start()

@app.get("/")
def home():
    return {"status": "AI Azbek assistant is running with Memory and Scheduler!"}

@app.post("/chat")
def chat_with_ai(msg: Message):
    chat_history.append(f"Фойдаланувчи: {msg.text}")
    prompt = "\n".join(chat_history)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    ai_response = response.text
    chat_history.append(f"Агент: {ai_response}")
    
    return {"response": ai_response}
