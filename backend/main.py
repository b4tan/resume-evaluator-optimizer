from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
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
import atexit
from docx import Document
import gc
import io
import zipfile
from fastapi import HTTPException
import os
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") 

# Initialize FastAPI app and middleware to connect to ReactJs front end
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=API_KEY)

# Load sentence-transformer model for vector embeddings 
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

# FAISS Index for storing vector embeddings
faiss_index = faiss.IndexFlatL2(384)

# Convert docx to text
def convert_docx_to_text(docx_bytes):
    """Extract text from a DOCX file."""
    with io.BytesIO(docx_bytes) as file_stream:
        doc = Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

# Convert PDF to text
def convert_pdf_to_text(pdf_bytes):
    """Extract text from a PDF file."""
    pdf_doc = fitz.open("pdf", pdf_bytes) 
    text = "\n".join(page.get_text("text") for page in pdf_doc)
    return text.strip()

# Evaluate Resume
def evaluate_resume(resume_text, job_desc):
    """Evaluate the resume based on job fit, comparing with past optimizations."""
    db = SessionLocal()
    
    # Retrieve past optimized resumes
    try:
        past_resumes = db.query(Resume).filter(Resume.job_description == job_desc).all()    
        past_optimized_texts = [r.optimized_resume for r in past_resumes]
    finally:
        db.close()
        gc.collect()

    prompt_template = PromptTemplate(
        input_variables=["resume", "job_description", "past_resumes"],
        template="Evaluate the following resume based on the job description. Also, compare it to past optimized resumes and suggest improvements. If it's better than past resumes, highlight why. Format as structured plain text without markdown. \n\nJob Description:\n{job_description}\n\nPast Optimized Resumes:\n{past_resumes}\n\nResume:\n{resume}"
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    evaluation = chain.run({"resume": resume_text, "job_description": job_desc, "past_resumes": past_optimized_texts})

    return evaluation


# Optimize Resume
def optimize_resume(resume_text, job_desc, evaluation):
    """Generate an optimized version of the resume using iterative self-improvement."""
    prompt_template = PromptTemplate(
        input_variables=["resume", "job_description", "evaluation"],
        template="Improve the following resume based on the provided evaluation. Ensure the new version aligns better with the job description while maintaining clarity and professionalism. If improvements can still be made, provide feedback on what should change. Format as structured plain text without markdown code. \n\nJob Description:\n{job_description}\n\nEvaluation:\n{evaluation}\n\nResume:\n{resume}"
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    optimized_resume = resume_text 
    # Feedback loop
    for _ in range(3): 
        evaluation = evaluate_resume(optimized_resume, job_desc)  # Evaluate new version
        new_version = chain.run({"resume": optimized_resume, "job_description": job_desc, "evaluation": evaluation})
        
        # If the new version is similar to the previous one, stop iterating
        if new_version.strip() == optimized_resume.strip():
            break
        optimized_resume = new_version

    return optimized_resume

# Hybrid Scoring Function
def calculate_hybrid_score(resume_text, job_desc):
    """Compute a hybrid resume score combining cosine similarity and LLM-based evaluation."""
    
    # Cosine Similarity Score (0-50)
    resume_embedding = embedding_model.encode(resume_text).astype(np.float32)
    job_embedding = embedding_model.encode(job_desc).astype(np.float32)
    similarity_score = np.dot(resume_embedding, job_embedding) / (np.linalg.norm(resume_embedding) * np.linalg.norm(job_embedding))
    similarity_score_scaled = similarity_score * 50  # Scale to 0-50 range

    # LLM-Based Score (0-50)
    scoring_prompt = PromptTemplate(
        input_variables=["resume", "job_description"],
        template="Evaluate the following resume based on the job description. Assign a numerical score from 0 to 50 based on alignment with the job requirements, clarity, structure, and impact. Return only the score as an integer.\n\nJob Description:\n{job_description}\n\nResume:\n{resume}"
    )
    
    chain = LLMChain(llm=llm, prompt=scoring_prompt)
    llm_score = chain.run({"resume": resume_text, "job_description": job_desc}).strip()

    # Ensure LLM returns a valid number
    try:
        llm_score = float(llm_score)
        llm_score = max(0, min(50, llm_score))  # Clamp between 0-50
    except ValueError:
        llm_score = similarity_score

    # Final Score
    final_score = similarity_score_scaled + llm_score
    return round(final_score, 2)

# Process and store a single resume with an Agentic workflow
def process_resume(resume_content, filename, content_type, job_desc, db):
    global embedding_model

    if content_type == "application/pdf":
        resume_text = convert_pdf_to_text(resume_content)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = convert_docx_to_text(resume_content)
    else:
        resume_text = resume_content.decode("utf-8")

    # Generate embeddings
    resume_embedding = embedding_model.encode(resume_text).astype(np.float32)
    job_embedding = embedding_model.encode(job_desc).astype(np.float32)
    
    # Compute similarity score
    similarity_score = np.dot(resume_embedding, job_embedding) / (np.linalg.norm(resume_embedding) * np.linalg.norm(job_embedding))

    # Evaluate resume
    evaluation = evaluate_resume(resume_text, job_desc)

    # Agentic Decision-Making
    decision_prompt = PromptTemplate(
        input_variables=["evaluation"],
        template="Based on the following evaluation, should the resume be optimized further? Reply with 'YES' if improvements are needed, or 'NO' if the resume is already good.\n\nEvaluation:\n{evaluation}"
    )
    
    decision_chain = LLMChain(llm=llm, prompt=decision_prompt)
    decision = decision_chain.run({"evaluation": evaluation}).strip()

    # If the model thinks the resume needs optimization, iterate
    if "YES" in decision:
        optimized_resume = optimize_resume(resume_text, job_desc, evaluation)
    else:
        optimized_resume = resume_text 

    # Store the processed resume
    new_resume = Resume(
        filename=filename,
        text_content=resume_text,
        optimized_resume=optimized_resume,
        job_description=job_desc,
        embedding=resume_embedding.tobytes(),
        score=similarity_score,
        evaluation=evaluation,
    )
    db.add(new_resume)
    db.commit()
    gc.collect()


# Handle resume upload
@app.post("/upload_resumes/")
async def upload_resumes(
    resumes: list[UploadFile] = File(...),
    job_description: str = Form(...)
):
    db = SessionLocal()

    try:
        db.query(Resume).delete()  
        db.commit()
        
        for resume in resumes:
            filename = resume.filename.lower()
            content = await resume.read()

            if filename.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(content), "r") as zip_ref:
                    for file_info in zip_ref.infolist():
                        extracted_filename = file_info.filename
                        extracted_filename = os.path.normpath(extracted_filename).lower()

                        # Skip files that are irrelevant
                        if file_info.is_dir() or any(part.startswith(("__", "._", ".ds_store")) for part in extracted_filename.split(os.sep)):
                            continue

                        # Process only .pdf, .txt, and .docx files
                        if extracted_filename.endswith(".pdf"):
                            file_type = "application/pdf"
                        elif extracted_filename.endswith(".docx"):
                            file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        else:
                            continue 

                        with zip_ref.open(file_info) as file:
                            process_resume(file.read(), extracted_filename, file_type, job_description, db)

            elif filename.endswith((".pdf", ".docx")):
                file_type = (
                    "application/pdf" if filename.endswith(".pdf") else
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                process_resume(content, filename, file_type, job_description, db)

        return {"message": "Resumes uploaded and processed successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
        gc.collect()
        

# Returns resume metadata ranked
@app.get("/get_ranked_resumes/")
async def get_ranked_resumes():
    db = SessionLocal()
    try:
        ranked_resumes = db.query(Resume).order_by(Resume.score.desc()).all()
    finally:
        db.close()
        gc.collect()
    
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

# Handle download
@app.get("/download_optimized/{filename}")
async def download_optimized_resume(filename: str):
    db = SessionLocal()
    resume = db.query(Resume).filter(Resume.filename == filename).first()
    db.close()

    if not resume or not resume.optimized_resume:
        return {"error": "Optimized resume not found."}

    optimized_filename = filename.replace(".pdf", "_optimized.txt")

    return Response(
        content=resume.optimized_resume,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={optimized_filename}"}
    )

