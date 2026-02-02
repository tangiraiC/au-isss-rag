import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Optional, List, Any
from dotenv import load_dotenv

# Load env variables
load_dotenv()

class PlaceholderLLM(LLM):
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return "Generic PlaceHolder: I found relevant documents but I cannot synthesize an answer without a real model API key. Please check the 'source_documents' below."

    @property
    def _llm_type(self) -> str:
        return "placeholder"

class RAGChain:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.vector_store_path = os.path.join(data_dir, "faiss_index")
        # Use a local embedding model to avoid API costs/limits for retrieval
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = self._initialize_db()
        
        # Initialize LLM (DeepSeek via OpenAI interface)
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            print("Initializing ChatOpenAI with DeepSeek...")
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                openai_api_key=deepseek_api_key,
                openai_api_base="https://api.deepseek.com",
                temperature=0.7
            )
        else:
            print("DEEPSEEK_API_KEY not found. Using PlaceholderLLM.")
            self.llm = PlaceholderLLM()

    def _load_documents(self):
        docs = []
        isss_path = os.path.join(self.data_dir, 'isss_data.csv')
        if os.path.exists(isss_path):
            df_isss = pd.read_csv(isss_path)
            for _, row in df_isss.iterrows():
                content = f"{row.get('Section', '')}: {row.get('Text', '')}"
                metadata = {"source": row.get('Source URL', ''), "type": "web"}
                docs.append(Document(page_content=content, metadata=metadata))

        rag_path = os.path.join(self.data_dir, 'rag_data.csv')
        if os.path.exists(rag_path):
            df_rag = pd.read_csv(rag_path)
            for _, row in df_rag.iterrows():
                content = f"{row.get('context', '')}\n{row.get('text', '')}"
                metadata = {"source": row.get('source', ''), "type": "document"}
                docs.append(Document(page_content=content, metadata=metadata))
        return docs

    def _initialize_db(self):
        if os.path.exists(self.vector_store_path):
            print("Loading existing FAISS index...")
            return FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
        
        print("Creating new FAISS index...")
        docs = self._load_documents()
        if not docs:
            return None
        db = FAISS.from_documents(docs, self.embeddings)
        db.save_local(self.vector_store_path)
        return db

    def search(self, query, top_k=5):
        if not self.db:
            return []
        
        # 1. Retrieve
        results = self.db.similarity_search_with_score(query, k=top_k)
        
        formatted_results = []
        context_text = ""
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "type": doc.metadata.get("type", "unknown"),
                "score": float(score)
            })
            # Truncate content for generation to avoid excessive token usage/latency
            truncated_content = doc.page_content[:4000] + "..." if len(doc.page_content) > 4000 else doc.page_content
            context_text += f"\nSource: {doc.metadata.get('source', 'unknown')}\nContent: {truncated_content}\n"

        # 2. Generate Answer
        if isinstance(self.llm, PlaceholderLLM):
            answer = self.llm._call(query)
        else:
            # Create a prompt for Llama
            prompt_template = """You are a helpful and professional academic advisor for American University International Student & Scholar Services (ISSS).
Start your response by explicitly stating: "Note: I am an AI assistant, not a human advisor. This information may not be 100% accurate."

Use the following pieces of retrieved context to answer the student's question.
1. Provide a COMPREHENSIVE and DETAILED answer.
2. If the context contains multiple steps, requirements, or lists, include ALL of them.
3. If the answer is not explicitly in the context, state that you don't have that information.

Context:
{context}

Question:
{question}

Answer:"""
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            chain = prompt | self.llm
            response = chain.invoke({"context": context_text, "question": query})
            answer = response.content

        return {
            "results": formatted_results,
            "answer": answer
        }

if __name__ == "__main__":
    chain = RAGChain("../../processed_data")
    print(chain.search("OPT"))
