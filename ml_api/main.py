from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
import uvicorn
from chroma_utils import vector_store
import uuid
from langchain_groq import ChatGroq

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.3-70b-versatile"
)

app = FastAPI(
    title="HireIQ AI Engine",
    description="Microservice for resume-job matching",
    version="1.0.0"
)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class MatchRequest(BaseModel):
    candidate_name: str
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
    vector_store.add_texts(
    texts=[data.resume_text],
    metadatas=[{
    "candidate_name": data.candidate_name,
    "category": "Software Engineer"
    }],
    ids=[str(uuid.uuid4())])
    return {"match_score": score}

@app.get("/search")
def search_resumes(query: str):
    results = vector_store.similarity_search(query=query, k=3)

    retrieved_resumes = []

    for doc in results:
        retrieved_resumes.append({
            "candidate_name": doc.metadata.get("candidate_name"),
            "category": doc.metadata.get("category")
        })

    return {"results": retrieved_resumes}

@app.get("/rag")
def rag_query(query:str):
    results=vector_store.similarity_search(query=query,k=2)

    context="\n\n".join([doc.page_content for doc in results])

    prompt=f"""
    You are an expert AI recruiter assistant.

    Analyze the retrieved resumes and answer professionally.

    Return:
    1. Best candidate
    2. Matching skills
    3. Strengths
    4. Missing skills
    5. Final recommendation

    Recruiter Query:
    {query}

    Resume Context:
    {context}
    """

    response=llm.invoke(prompt)

    return {"response":response.content}

@app.get("/rank")
def rank_candidates(jd:str):
    results=vector_store.similarity_search_with_score(jd,k=5)

    ranked_candidates=[]

    for doc,score in results:
        ranked_candidates.append({
            "candidate_name":doc.metadata.get("candidate_name"),
            "score":round(100 / (1 + score))
        })

    ranked_candidates=sorted(
        ranked_candidates,
        key=lambda x:x["score"],
        reverse=True
    )

    return {"rankings":ranked_candidates}

@app.get("/feedback")
def ats_feedback(query:str):
    results=vector_store.similarity_search(query=query,k=1)

    context="\n\n".join([doc.page_content for doc in results])

    prompt=f"""
    You are an expert ATS optimization assistant.

    Analyze the candidate resume against the job requirement.

    Return:
    1. ATS Match Analysis
    2. Missing Skills
    3. Resume Strengths
    4. Weak Areas
    5. Improvement Suggestions
    6. Keywords To Add
    7. Final ATS Recommendation

    Job Requirement:
    {query}

    Resume:
    {context}
    """

    response=llm.invoke(prompt)

    return {"feedback":response.content}

@app.get("/interview")
def generate_interview_questions(query:str):
    results=vector_store.similarity_search(query=query,k=1)
    context="\n\n".join([doc.page_content for doc in results])
    prompt=f"""
    You are an expert technical interviewer.

    Generate interview questions based on the candidate resume and job requirement.

    Return:
    1. Technical Questions
    2. Project-Based Questions
    3. Problem-Solving Questions
    4. HR Questions
    5. Follow-Up Questions

    Job Requirement:
    {query}

    Candidate Resume:
    {context}
    """
    response=llm.invoke(prompt)
    return {"interview_questions":response.content}

@app.get("/recruiter-interview")
def recruiter_interview(query:str):
    prompt=f"""
    You are an expert technical interviewer.
    Generate:

    1. Technical Questions
    2. HR Questions
    3. System Design Questions
    4. Scenario-Based Questions
    5. Follow-Up Questions

    based on this job description:
    {query}
    """
    response=llm.invoke(prompt)
    return {
        "interview_questions":response.content
    }

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8001)

