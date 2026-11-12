import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="AI Azbek Personal Assistant")

# Телефон иловаси (APK) бемалол уланиши учун рухсат
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API миясини улаш
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Вазифалар ва эслатмалар хотираси (вақтинчалик, кейин базага улаймиз)
tasks_db = []

# Вақтни кузатиб борувчи мустақил режалаштирувчи (Scheduler)
scheduler = BackgroundScheduler()
scheduler.start()

class UserMessage(BaseModel):
    text: str

class ReminderCreate(BaseModel):
    title: str
    run_at: str  # Формат: YYYY-MM-DD HH:MM

@app.get("/")
def home():
    return {"status": "online", "assistant": "AI Azbek", "time": str(datetime.now())}

# 1-МОДУЛЬ: Асосий суҳбат ва ақлли ёрдамчи
@app.post("/chat")
def chat_with_agent(msg: UserMessage):
    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY ўрнатилмаган!")
    
    system_prompt = (
        "Сен Азизбекаканинг шахсий AI ассистентисан. Исминг AI Azbek. "
        "Ҳар доим қисқа, аниқ, дўстона ва ўзбек тилида (кирилл ёзувида) жавоб бер. "
        "Сен вазифаларни режалаштириш, эслатиш ва келажакда дастурлаш ҳамда видео яратишда ёрдам берасан."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_prompt}\n\nФойдаланувчи: {msg.text}"
    )
    return {"reply": response.text}

# 2-МОДУЛЬ: Эслатма ва қўнғироқ учун вазифа қўшиш
@app.post("/add-task")
def add_task(task: ReminderCreate):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "run_at": task.run_at,
        "triggered": False
    }
    tasks_db.append(new_task)
    return {"message": "Вазифа сақланди", "task": new_task}

# Телефон иловаси қўнғироқ вақти келганини текширадиган манзил
@app.get("/check-calls")
def check_calls():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    due_tasks = []
    for t in tasks_db:
        if not t["triggered"] and t["run_at"] <= now_str:
            t["triggered"] = True
            due_tasks.append(t)
    return {"incoming_calls": due_tasks}
