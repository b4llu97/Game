from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logic

app = FastAPI(title="Jarvis Orchestrator", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    response: str
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]

@app.get("/")
def root():
    return {"service": "Jarvis Orchestrator", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        result = logic.process_query(
            query=request.query,
            conversation_history=request.conversation_history
        )
        
        return QueryResponse(
            response=result["response"],
            tool_calls=result["tool_calls"],
            tool_results=result["tool_results"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )
