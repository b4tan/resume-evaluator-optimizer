from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as llm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import shutil
import zipfile
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") 

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=API_KEY)

# Load sentence-transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Setup DB
DATABASE_URL = "sqlite:///./resumes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    text_content = Column(String)  # Original resume
    optimized_resume = Column(String)  # Improved resume
    job_description = Column(String)  # Job description
    embedding = Column(LargeBinary)  # Resume embedding
    score = Column(Float)  # Score based on job fit
    evaluation = Column(String)  # LLM feedback

Base.metadata.create_all(bind=engine)

# FAISS Index for storing resume embeddings
faiss_index = faiss.IndexFlatL2(384)

# Convert PDF to text
def convert_pdf_to_text(pdf_bytes):
    """Extract text from a PDF file."""
    pdf_doc = fitz.open("pdf", pdf_bytes) 
    text = "\n".join(page.get_text("text") for page in pdf_doc)
    return text.strip()

# Process and store a single resume
def process_resume(resume_content, filename, content_type, job_desc, db):
    resume_text = convert_pdf_to_text(resume_content) if content_type == "application/pdf" else resume_content.decode("utf-8")
    
    # Generate embeddings
    resume_embedding = embedding_model.encode(resume_text).astype(np.float32)
    job_embedding = embedding_model.encode(job_desc).astype(np.float32)

    # Compute similarity score
    similarity_score = np.dot(resume_embedding, job_embedding) / (np.linalg.norm(resume_embedding) * np.linalg.norm(job_embedding))

    # Generate optimized resume using LLM
    prompt_template = PromptTemplate(input_variables=["resume", "job_description"], 
                                     template="Improve the following resume to fit this job:\n\nJob: {job_description}\n\nResume: {resume}")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    optimized_resume = chain.run({"resume": resume_text, "job_description": job_desc})

    # Check if the filename already exists
    existing_resume = db.query(Resume).filter(Resume.filename == filename).first()

    if existing_resume:
        # If resume exists, update it
        existing_resume.text_content = resume_text
        existing_resume.optimized_resume = optimized_resume
        existing_resume.job_description = job_desc
        existing_resume.embedding = resume_embedding.tobytes()
        existing_resume.score = similarity_score
        db.commit()
    else:
        # If resume does not exist, insert a new one
        new_resume = Resume(
            filename=filename,
            text_content=resume_text,
            optimized_resume=optimized_resume,
            job_description=job_desc,
            embedding=resume_embedding.tobytes(),
            score=similarity_score,
        )
        db.add(new_resume)
        db.commit()
        print(f"✅ Added new resume: {filename}")


@app.post("/upload_resumes/")
async def upload_resumes(
    resumes: list[UploadFile] = File(...),
    job_description: str = Form(...)
):
    """Uploads multiple resumes (PDFs or a ZIP file) and processes them with a job description."""
    db = SessionLocal()
    extracted_files = []
    
    # Ensure directory exists
    os.makedirs("./original_resumes/", exist_ok=True)
    
    for resume in resumes:
        if resume.filename.endswith(".zip"):
            zip_path = f"./original_resumes/{resume.filename}"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall("./original_resumes/")
                extracted_files.extend([f"./original_resumes/{f}" for f in zip_ref.namelist()])
        else:
            file_path = f"./original_resumes/{resume.filename}"
            extracted_files.append(file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

    # Process each extracted file
    for file_path in extracted_files:
        with open(file_path, "rb") as file:
            content = file.read()
            process_resume(content, os.path.basename(file_path), "application/pdf", job_description, db)

    db.close()
    return {"message": "Resumes uploaded and processed successfully."}


@app.get("/get_ranked_resumes/")
async def get_ranked_resumes():
    db = SessionLocal()
    ranked_resumes = db.query(Resume).order_by(Resume.score.desc()).all()
    db.close()
    
    if not ranked_resumes:
        return {"message": "No resumes available.", "resumes": []}

    return {
        "total_candidates": len(ranked_resumes),
        "resumes": [
            {
                "filename": r.filename,
                "original_resume": r.text_content,
                "optimized_resume": r.optimized_resume,
                "evaluation": r.evaluation,
                "score": r.score,
            }
            for r in ranked_resumes
        ]
    }

