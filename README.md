This tool uses an agentic approach to evaluate and optimize resumes based on a job description.

# Overview of Design:
1. File upload: Resumes are expected to be PDFs, DOCX files, and ZIP archives.
2. Storage: Stores raw text in a SQLite database and vector embeddings in a FAISS index.
3. LLM Processing: Utilizes a multi-step workflow inspired by Anthropic’s "Building Effective Agents" (Evaluator-optimizer).
   * Parsing – Extracts meaningful content from documents.
   * Evaluation & Optimization – The system iteratively evaluates its outputs and refines them based on feedback.
   * Scoring & Ranking – Hybrid ranking system combining cosine similarity and LLM-generated scores.
5. Frontend: Displays original and processed documents with evaluation results.
6. Scoring & Ranking: Hybrid ranking system combining cosine similarity and LLM-generated scores

# Architechture diagram
```
User Uploads Document(s) ───► Backend (FastAPI) ───► Document Parsing  
    │                                │                      │  
    │                                │                      ├─► PDF/DOCX Processing  
    │                                │                      ├─► Text Extraction  
    │                                │                      ├─► Store Raw Text in Database  
    │                                │                      ├─► Generate Vector Embeddings (FAISS)  
    │                                │  
    │                                ├─► LLM Processing Pipeline  
    │                                │      ├─► Step 1: Evaluate Document (LLM Feedback)  
    │                                │      ├─► Step 2: Optimize Document (Evaluator-Optimizer Iteration)  
    │                                │      ├─► Step 3: Hybrid Scoring (Cosine Similarity + LLM Scoring)  
    │                                │      ├─► Step 4: Agentic Decision-Making (Refinement Needed?)  
    │                                │  
    │                                ├─► Store Processed Output in Database  
    │  
    │  
    ├─► Retrieve Processed Data ───► Frontend (React)  
    │           │  
    │           ├─► Display Original Document  
    │           ├─► Display Evaluated & Optimized Document  
    │           ├─► Show Scoring & Ranking Results  
    │           ├─► User Interaction (Download, Navigate)  
    │  
    └─► User Downloads Optimized Document  
```

# Step-by-step setup instructions

## Clone this repo
git clone (https://github.com/b4tan/resume-evaluator-optimizer.git)

## To run backend server

### Install dependencies and create venv
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt

### Setup enviroment vairables
Create a .env file and add GEMINI_API_KEY=<your_api_key>
### Run backend
cd backend
uvicorn main:app --reload

## To run frontend server

### Install dependencies
npm i

### Run frontend
cd client
npm run start

## Accessing/Utilizing the web app
Once both the frontend and backend servers are running, navigate to the hosted web application. If running locally, visit http://localhost:3000/ in your browser. From there, you can upload resumes and a job description to process and analyze them.

## Resources:
[link] https://python.langchain.com/docs/concepts/prompt_templates/
[link] https://python.langchain.com/v0.1/docs/modules/chains/
[link] https://medium.com/towards-agi/how-to-use-gemini-with-langchain-a-step-by-step-guide-6f79c229505e
[link] https://engineering.fb.com/2017/03/29/data-infrastructure/faiss-a-library-for-efficient-similarity-search/
[link] https://pypi.org/project/sentence-transformers/
[link] https://medium.com/@sandyjtech/creating-a-database-using-python-and-sqlalchemy-422b7ba39d7e
[link] https://sakilansari4.medium.com/unleashing-the-power-of-sentence-transformers-revolutionising-semantic-search-and-sentence-edc22c8180ed

