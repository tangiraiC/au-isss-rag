# AU ISSS RAG Application

A Retrieval-Augmented Generation (RAG) system built to navigate and query American University's International Student & Scholar Services (ISSS) handbooks and policies.

## 📖 Overview

This project is a full-stack AI application designed to make university policies accessible and queryable. It features a robust backend pipeline that scrapes the AU ISSS website and processes various document formats (PDF, DOCX) into a searchable vector index using FAISS and local embeddings. The backend, built with FastAPI and LangChain, serves a modern React frontend where users can ask questions and receive context-aware answers derived directly from the official handbooks.

## ✨ Features

- **Automated Data Acquisition**: Custom web scraper recursively crawls the AU ISSS website.
- **Document Processing**: Ingests and normalizes PDF and Word documents with hierarchical chunking.
- **RAG Pipeline**: Retrieves relevant context using FAISS vector search and HuggingFace embeddings (`all-MiniLM-L6-v2`).
- **Modern Search Interface**: Responsive React frontend with markdown support for rich answers.
- **Privacy First**: Uses local embeddings and vector storage; no external API keys required for the core retrieval logic.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain, FAISS, SentenceTransformers
- **Frontend**: React, Vite, Axios, Tailwind CSS (implied/if used)
- **Data Processing**: BeautifulSoup4, PyPDF, python-docx

## 📂 Project Structure

```bash
├── rag_app/
│   ├── backend/          # FastAPI application & RAG logic
│   └── frontend/         # React application
├── raw_documents/        # Input PDFs and DOCX files
├── processed_data/       # Generated CSVs and FAISS index (not in repo)
├── scraper.py            # Web scraper script
└── batch_converter.py    # Document processor script
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/tangiraiC/au-isss-rag.git
cd au-isss-rag
```

### 2. Backend Setup

Create a virtual environment and install dependencies:

```bash
cd rag_app/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note**: If `requirements.txt` is missing, ensure you install: `fastapi uvicorn langchain sentence-transformers faiss-cpu pypdf python-docx beautifulsoup4 requests`

Create a `.env` file in `rag_app/backend/` if needed (e.g., for LLM API keys if extending beyond local retrieval).

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd ../frontend
npm install
```

### 4. Data Generation (First Run Only)

Before running the app, you need to populate the vector index:

1.  **Scrape Data** (Optional if you only have local docs):
    ```bash
    # From project root
    python scraper.py
    ```
2.  **Process Documents**:
    Ensure your PDFs/DOCX files are in `raw_documents/`.
    ```bash
    python batch_converter.py
    ```
    This will generate `processed_data/` containing the FAISS index.

## 🏃‍♂️ Running the Application

### Start the Backend

```bash
cd rag_app/backend
# Activate venv if not active
uvicorn main:app --reload --port 8001
```

### Start the Frontend

In a new terminal:

```bash
cd rag_app/frontend
npm run dev
```

Open your browser to `http://localhost:5173`.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.
