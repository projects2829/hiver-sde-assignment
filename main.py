from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from openai import OpenAI

app = FastAPI(title="AppleSupport AI Agent API")

# Direct CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

INTENT_TAXONOMY = [
    "account_access",
    "device_hardware",
    "software_update",
    "billing_subscription",
    "connectivity_sync",
    "general_query"
]

SYSTEM_PROMPT = f"""You are an AI Support Agent for @AppleSupport on Twitter.
Analyze the customer's tweet and generate a structured JSON response.

Intents allowed: {', '.join(INTENT_TAXONOMY)}

Rules for Escalation:
- Set 'escalate' to true IF the query involves unauthorized billing, financial refund requests, severe user frustration/abuse, or personal security breaches (hacked Apple ID).
- Otherwise, set 'escalate' to false.

Response Guidelines:
- Draft a polite, concise reply (< 280 characters).
- Suggest official help links (e.g., support.apple.com) or standard troubleshooting.
"""

class TweetRequest(BaseModel):
    tweet: str

@app.get("/")
def home():
    return {"status": "AppleSupport AI Agent API is running!"}

# Single unified route for both trailing slash variants
@app.api_route("/api/chat", methods=["GET", "POST"])
@app.api_route("/api/chat/", methods=["GET", "POST"])
async def chat_endpoint(payload: TweetRequest = None):
    if not payload or not payload.tweet.strip():
        return {"response": {"message": "Please enter a valid tweet query.", "intent": "general_query", "escalate": False}}
    
    try:
        user_payload = f'Customer Tweet: "{payload.tweet}"'
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_payload}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
