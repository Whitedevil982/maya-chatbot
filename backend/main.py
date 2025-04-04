from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load environment variables
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Missing GOOGLE_API_KEY in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# FastAPI setup
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom responses
CUSTOM_INPUTS = {
    "your name": "My name is Maya.",
    "your creator": "My creator is Mridul Gupta.",
    "made you": "I was made by Mridul Gupta.",
    "create you": "I was created by Mridul Gupta.",
    "who are you": "I am Maya, the chatbot."
}

# Request model
class ChatRequest(BaseModel):
    message: str
    history: list[str] = []

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    user_input = chat_request.message
    history = chat_request.history

    # Check custom responses first
    for key, response in CUSTOM_INPUTS.items():
        if key in user_input.lower():
            new_history = history + [f"User: {user_input}", f"Maya: {response}"]
            return {"response": response, "history": new_history}

    # Generate AI response
    try:
        formatted_history = "\n".join(history[-10:])  # Keep last 10 messages
        response = model.generate_content(
            f"Previous conversation:\n{formatted_history}\nUser: {user_input}\nMaya:"
        )
        
        if response.candidates:
            ai_response = response.candidates[0].content.parts[0].text.strip()
        else:
            ai_response = "I'm not sure how to respond to that."

        new_history = history + [f"User: {user_input}", f"Maya: {ai_response}"]
        return {"response": ai_response, "history": new_history}

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating response: {str(e)}"
        )