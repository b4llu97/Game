from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import database
import tools
from database import get_db, init_db

app = FastAPI(title="Jarvis Toolserver", version="1.0.0")

init_db()

class FactRequest(BaseModel):
    value: str

class FactResponse(BaseModel):
    key: str
    value: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5

class DocumentRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

@app.get("/")
def root():
    return {"service": "Jarvis Toolserver", "status": "running"}

@app.get("/v1/tools")
def get_tools():
    return {"tools": tools.get_tool_definitions()}

@app.get("/v1/facts/{key}", response_model=FactResponse)
def get_fact(key: str, db: Session = Depends(get_db)):
    fact = database.get_fact(db, key)
    if not fact:
        raise HTTPException(status_code=404, detail=f"Fact with key '{key}' not found")
    return fact.to_dict()

@app.put("/v1/facts/{key}", response_model=FactResponse)
def set_fact(key: str, request: FactRequest, db: Session = Depends(get_db)):
    fact = database.set_fact(db, key, request.value)
    return fact.to_dict()

@app.delete("/v1/facts/{key}")
def delete_fact(key: str, db: Session = Depends(get_db)):
    success = database.delete_fact(db, key)
    if not success:
        raise HTTPException(status_code=404, detail=f"Fact with key '{key}' not found")
    return {"message": f"Fact '{key}' deleted successfully"}

@app.get("/v1/facts", response_model=List[FactResponse])
def list_facts(db: Session = Depends(get_db)):
    facts = database.list_all_facts(db)
    return [fact.to_dict() for fact in facts]

@app.post("/v1/search")
def search_documents(request: SearchRequest):
    results = tools.search_docs(request.query, request.n_results)
    return {"query": request.query, "results": results}

@app.post("/v1/documents")
def add_document(request: DocumentRequest):
    success = tools.add_document(request.text, request.metadata)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add document")
    return {"message": "Document added successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
