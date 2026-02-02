# RAG Application Process & Architecture

This document outlines the architecture and process flow of the Retrieval-Augmented Generation (RAG) application built for the AU ISSS data.

## Process Overview

1. **Data Acquisition**:
    - **Scraping**: `scraper.py` recursively crawls `www.american.edu/student-affairs/isss/` to collect web content.
    - **Documents**: PDF and Word documents (`raw_documents/`) containing handbooks and policies.

2. **Data Processing**:
    - **Normalization**: `batch_converter.py` ingests PDFs (using `pypdf`) and Word docs (using `python-docx`).
    - **Chunking**: Documents are split into logical chunks (paragraphs, pages) with hierarchical context (headings).
    - **Output**: Cleaned data is stored in `processed_data/` as CSV files (`isss_data.csv`, `rag_data.csv`).

3. **Indexing (Backend Start)**:
    - **Loading**: `RAGChain` loads the CSVs.
    - **Embedding**: `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`) converts text chunks into vector embeddings.
    - **Storage**: `FAISS` vector store indexes these embeddings locally for fast similarity search.

4. **Retrieval & Query**:
    - **User Query**: User asks a question in the React Frontend.
    - **Search**: Backend uses LangChain to embed the query and retrieve top-k similar chunks from FAISS.
    - **Response**: The application returns the retrieval results (and optionally synthesizes an answer if an LLM is connected).

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI (Port 8001)
- **Logic**: `rag_app/backend/chain.py`
    - Uses **LangChain** for RAG orchestration.
    - Uses **FAISS** for vector storage.
    - Uses **SentenceTransformers** for local embeddings (no API keys required).
- **API**: `rag_app/backend/main.py` exposes a `/query` endpoint.

### Frontend (React/Vite)
- **Framework**: React (Port 5173/5174)
- **Logic**: `rag_app/frontend/src/`
    - `App.jsx`: Main interface.
    - `api.js`: Communicates with backend.
- **Styling**: Clean, American University-themed CSS.

## Directory Structure
```
/Users/fibonacci/Documents/scrap/
├── raw_documents/            # Original PDFs and DOCX
├── processed_data/           # Scraped and Converted CSVs + FAISS Index
├── rag_app/
│   ├── backend/
│   │   ├── main.py           # FastAPI App
│   │   └── chain.py          # LangChain Logic
│   └── frontend/             # React App
├── scraper.py                # Web Scraper
└── batch_converter.py        # Document Processor
```
