from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

app = FastAPI(
    title="HireIQ AI Engine",
    description="Microservice for resume-job matching",
    version="1.0.0"
)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class MatchRequest(BaseModel):
    resume_text: str
    jd_text: str

@app.get("/")
def home():
    return {"message": "HireIQ AI Engine Running"}

@app.post("/match")
def match_score(data: MatchRequest):
    resume_embedding = model.encode([data.resume_text])
    jd_embedding = model.encode([data.jd_text])
    similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
    score = round(float(similarity) * 100, 2)
    return {"match_score": score}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
