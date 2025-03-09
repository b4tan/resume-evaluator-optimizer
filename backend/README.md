# Install dependencies and create venv
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload
