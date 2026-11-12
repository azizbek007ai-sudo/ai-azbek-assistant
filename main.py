import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
chat_history = []

class Message(BaseModel):
    text: str

scheduler = BackgroundScheduler()
def scheduled_job():
    print("Background job executed.")
scheduler.add_job(scheduled_job, 'interval', minutes=30)
scheduler.start()

html_content = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Azizbek</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #1a73e8; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; }
        #chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 80%; padding: 10px 15px; border-radius: 15px; line-height: 1.4; word-wrap: break-word; }
        .user { background: #1a73e8; color: white; align-self: flex-end; }
        .ai { background: white; color: #333; align-self: flex-start; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .input-area { display: flex; padding: 10px; background: white; border-top: 1px solid #ddd; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 20px; outline: none; font-size: 16px; }
        button { background: #1a73e8; color: white; border: none; padding: 12px 20px; margin-left: 10px; border-radius: 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">AI Azizbek is online! 🟢</div>
    <div id="chat-box">
        <div class="msg ai">Assalomu alaykum! Men AI Azizbekman. Sizga qanday yordam bera olaman?</div>
    </div>
    <div class="input-area">
        <input type="text" id="msg-input" placeholder="Xabar yozing..." autocomplete="off">
        <button onclick="sendMsg()">Yuborish</button>
    </div>
    <script>
        async function sendMsg() {
            const input = document.getElementById('msg-input');
            const text = input.value.trim();
            if (!text) return;
            
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
                const data = await response.json();
                chatBox.innerHTML += `<div class="msg ai">${data.response}</div>`;
            } catch (error) {
                chatBox.innerHTML += `<div class="msg ai">Xatolik yuz berdi!</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        document.getElementById('msg-input').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMsg();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return html_content

@app.post("/chat")
def chat_with_ai(msg: Message):
    chat_history.append(f"Фойдаланувчи: {msg.text}")
    prompt = "\n".join(chat_history)
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "system_instruction": "Сенинг исминг AI Azizbek. Сен Азизбекнинг шахсий сунъий интеллект ёрдамчисисан. Кимлигинг ёки исмингни сўрашса, ўзингни доим AI Azizbek деб таништир. Ҳеч қачон ўзингни Gemini деб атама."
        }
    )
    
    ai_response = response.text
    chat_history.append(f"Агент: {ai_response}")
    return {"response": ai_response}
