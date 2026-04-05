from fastapi import FastAPI 
from pydantic import BaseModel
from backend.rag_pipeline import check_fact
from typing import Optional


# Create a FastAPI instance
app = FastAPI()

class FactCheckRequest(BaseModel):
    text: str
    custom_context: Optional[str] = ""

# Define a path operation (route)
@app.get("/")
def read_root():
    return {"Hello": "AI Fact Checker is running!!"}

# Endpoint for checking data
@app.post("/fact-check")
async def check(message: FactCheckRequest):
    result = await check_fact(message.text, message.custom_context)
    return result

