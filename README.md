##AI Fact-Checking Bot (RAG-Powered) :

An intelligent fact-checking system that validates user claims against uploaded documents (PDF, DOCX, TXT, CSV) and a secondary knowledge base using Retrieval-Augmented Generation (RAG).

******************************
##Project Architecture :

Frontend: Streamlit (User interface, file processing, and result visualization).

Backend: FastAPI + Groq (Llama 3.3) + FAISS (Vector search and LLM reasoning).

******************************
##Setup & Installation
 
1. Prerequisites

Python 3.10+
A Groq API Key (Sign up at console.groq.com)

2. Environment Setup

# Clone the repository
git clone <your-repo-link>
cd "AI Fact-Checking Bot"

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit fastapi uvicorn groq sentence-transformers faiss-cpu pandas python-docx pypdf requests

3. API Configuration

Create a .env file in the root directory (or set environment variables):

GROQ_API_KEY=your_actual_api_key_here

******************************
##Running the Application

You must run both the backend and the frontend simultaneously in two separate terminals.

Step 1: Start the Backend (FastAPI)
The backend handles the vector search and LLM logic.

Bash
# From the project root
python -m uvicorn backend.main:app --reload

URL: http://localhost:8000

Note: Ensure your rag_pipeline.py has temperature=0.0 for consistent fact-checking.

Step 2: Start the Frontend (Streamlit)
The frontend handles file uploads and user interaction.

Bash
# Open a new terminal and activate venv
cd frontend
streamlit run app.py

URL: http://localhost:8501

******************************
##User Guide
Upload Documents: Use the sidebar to upload reference files (.pdf, .csv, .txt, or .docx).

Verify Extraction: Click the "View Raw Extracted Text" expander to ensure your files were read correctly.

Enter a Claim: Type a specific statement you want to verify (e.g., "The price of Widget B is 25.50").

Analyze Results:

Verdict: True, False, or Not Enough Information.

Confidence: Percentage of AI certainty.

Explanation: Contextual reasoning based strictly on the provided sources.

Sources: View the top matches retrieved from the internal database.

******************************
##Technical Details
Parsing Logic: Uses a "Marker-Based" extraction system (###BEGIN_JSON) to ensure LLM responses are parsed into valid UI elements without hallucinations.

Search: Utilizes sentence-transformers for semantic embeddings and FAISS for lightning-fast similarity search.

Precision: Structured prompts force the AI to prioritize "Primary Sources" (uploaded files) over its own internal training data to prevent "knowledge leakage."