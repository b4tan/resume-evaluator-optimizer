from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as llm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import fitz

# Load environment variables
load_dotenv()
# Initialize LLM
API_KEY = os.getenv("GEMINI_API_KEY")  # Ensure this is set in .env

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=API_KEY)
app = FastAPI()

# Use middleware to allow request from React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only allow requests from React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Convert PDF to text using PyMuPDF
def convert_pdf_to_text(pdf_bytes):
    """Extract text from a PDF file."""
    pdf_doc = fitz.open("pdf", pdf_bytes) 
    text = "\n".join(page.get_text("text") for page in pdf_doc)
    return text.strip()

# Define LangChain prompt templates
evaluate_prompt = PromptTemplate.from_template("""
resume = {resume}
job description = {job_description}

Evaluate the resume based on the job description and provide:
1. List strengths and weaknesses of candidate according to the job description.
2. Missing skills or requirements according to the job description.
3. A numerical score (0-100) rating the candidate's fit for the job (Assign to variable Score for easier parsing and make it in the last line).
""")

optimize_prompt = PromptTemplate.from_template("""
resume = {resume}
job description = {job_description}

Optimize the resume by improving wording and highlighting strengths while keeping it truthful. 
Ensure it matches the job description better and format it professionally.
""")

@app.post("/process/")
async def process_document(resume: UploadFile = File(...), job_description: str = Form(...), max_iterations: int = 3):
    """Processes a resume file, evaluates it, and optimizes it iteratively."""
    resume_content = await resume.read()  # Read file content

    # Check file type
    if resume.content_type == "application/pdf":
        resume_text = convert_pdf_to_text(resume_content)  # Convert PDF to text
    else:
        resume_text = resume_content.decode("utf-8")  # Decode text files

    evaluate_chain = LLMChain(llm=llm, prompt=evaluate_prompt)
    optimize_chain = LLMChain(llm=llm, prompt=optimize_prompt)

    iteration = 0
    best_score = 0
    best_resume = resume_text
    threshold = 85  

    while iteration < max_iterations:
        evaluation = evaluate_chain.run(resume=best_resume, job_description=job_description)

        # Extract score from evaluation text (assumes last line contains score)
        score_lines = evaluation.strip().split("\n")
        try:
            extracted_score = int(score_lines[-1].split()[-1])  # Extract numeric score from last line
        except ValueError:
            extracted_score = 50  # Default fallback score if parsing fails

        if extracted_score > best_score:
            best_score = extracted_score

        if extracted_score >= threshold:
            break  # Stop refining if target score is reached

        # Optimize the resume further
        best_resume = optimize_chain.run(resume=best_resume, job_description=job_description)
        iteration += 1

    return {"evaluation": evaluation, "optimized_resume": best_resume, "iterations": iteration}
