This tool uses an agentic approach to evaluate and optimize resumes based on a job description.
Overview of Design:
File upload: Resumes are expected to be PDFs, DOCX files, and ZIP archives.
Storage: Stores raw text in a SQLite database and vector embeddings in a FAISS index.
LLM Processing: Utilizes a multi-step workflow inspired by Anthropic’s "Building Effective Agents" (Evaluator-optimizer).
Frontend: Displays original and processed documents with evaluation results.
Scoring & Ranking: Hybrid ranking system combining cosine similarity and LLM-generated scores
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
cd frontend
npm run start