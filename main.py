import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class Message(BaseModel):
    text: str

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
    sys_inst = "Сенинг исминг AI Azizbek. Сен Азизбекнинг шахсий сунъий интеллект ёрдамчисисан. Кимлигинг ёки исмингни сўрашса, ўзингни доим AI Azizbek деб таништир. Ҳеч қачон ўзингни Gemini деб атама."
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=sys_inst
        )
        response = model.generate_content(msg.text)
        ai_response = response.text
    except Exception as e:
        ai_response = "Salom! Men AI Azizbekman. Hozir tarmoqda yuklama bor, lekin sizga yordam berishga tayyorman!"
    
    return {"response": ai_response}
