from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chain import RAGChain

app = FastAPI(title="ISSS RAG API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Chain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'processed_data')

rag_chain = RAGChain(DATA_DIR)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 6

class SearchResult(BaseModel):
    content: str
    source: str
    type: str
    score: float

class QueryResponse(BaseModel):
    results: List[SearchResult]
    answer: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "ISSS RAG API (LangChain) is running"}

@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    search_output = rag_chain.search(request.query, top_k=request.top_k)
    
    return {
        "results": search_output["results"],
        "answer": search_output["answer"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
