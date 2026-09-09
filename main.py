from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from test_agent import process_tweet

app = FastAPI(title="AppleSupport AI Agent API")

# Frontend se requests allow karne ke liye CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TweetRequest(BaseModel):
    tweet: str

@app.get("/")
def home():
    return {"status": "AppleSupport AI Agent API is running!"}

@app.post("/api/chat")
def chat_endpoint(payload: TweetRequest):
    if not payload.tweet.strip():
        raise HTTPException(status_code=400, detail="Tweet text cannot be empty")
    
    try:
        response = process_tweet(payload.tweet)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))