import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

# Телефонингизда очиш учун чиройли чат интерфейси (Web UI)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Azbek Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 90vh; justify-content: space-between; }
            h2 { text-align: center; color: #38bdf8; margin-bottom: 10px; }
            #chat-box { flex: 1; overflow-y: auto; background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }
            .msg { padding: 10px 14px; border-radius: 8px; max-width: 80%; line-height: 1.4; }
            .user { background: #0284c7; align-self: flex-end; }
            .ai { background: #334155; align-self: flex-start; }
            .input-area { display: flex; gap: 10px; }
            input { flex: 1; padding: 12px; border-radius: 8px; border: none; background: #334155; color: #fff; font-size: 16px; }
            button { padding: 12px 20px; background: #38bdf8; color: #0f172a; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }
        </style>
    </head>
    <body>
        <h2>AI Azbek Assistant</h2>
        <div id="chat-box"></div>
        <div class="input-area">
            <input type="text" id="msg-input" placeholder="Хабар ёзинг..." onkeypress="if(event.key === 'Enter') sendMsg()">
            <button onclick="sendMsg()">Юбориш</button>
        </div>

        <script>
            async function sendMsg() {
                const input = document.getElementById('msg-input');
                const chatBox = document.getElementById('chat-box');
                const text = input.value.trim();
                if(!text) return;

                chatBox.innerHTML += `<div class="msg user"><b>Сиз:</b> ${text}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const data = await res.json();
                    chatBox.innerHTML += `<div class="msg ai"><b>Агент:</b> ${data.response}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch(e) {
                    chatBox.innerHTML += `<div class="msg ai" style="color:red;">Хатолик юз берди!</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

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
