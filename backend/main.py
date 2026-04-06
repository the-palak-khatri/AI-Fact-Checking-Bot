from fastapi import FastAPI 
from pydantic import BaseModel
from rag_pipeline import check_fact
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origins=["*"],
    allow_origins=["*"],
)

# Create a FastAPI instance
app = FastAPI()

class FactCheckRequest(BaseModel):
    text: str
    custom_context: Optional[str] = ""

# Define a path operation (route)
@app.get("/")
def read_root():
    return {"Hello": "AI Fact Checker is running!!"}

@app.get("/health")
def health():
    return {
        "status":"alive"
    }

# Endpoint for checking data
@app.post("/fact-check")
async def check(message: FactCheckRequest):
    result = await check_fact(message.text, message.custom_context)
    return result

