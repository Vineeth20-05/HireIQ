from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import uvicorn
from chroma_utils import vector_store, client, embedding_model
from langchain_chroma import Chroma
import uuid
from langgraph_workflow import workflow
from llm_config import llm

hf_token = os.getenv("HF_TOKEN")

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
    user_id: str
    role: str

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
    "category": "Software Engineer",
    "user_id":data.user_id,
    "role":data.role
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
def rag_query(query: str, user_id: str):
    result = workflow.invoke({
        "query": query,
        "user_id": user_id
    })
    return {"response": result["final_response"]}


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
def ats_feedback(candidate_name:str,query:str):
    results = vector_store.similarity_search(
        query=query,
        k=5
    )
    context = ""
    for doc in results:
        if doc.metadata.get("candidate_name") == candidate_name:
            context = doc.page_content
            break

    prompt = f"""
    You are a senior technical recruiter working at a top product-based company.

    Your task is to evaluate the candidate resume against the provided job description exactly like a real recruiter performing ATS screening.

    Evaluation Guidelines:
    - Be concise and highly practical
    - Focus only on hiring-relevant insights
    - Avoid generic AI explanations
    - Prioritize technical alignment, experience relevance, and project quality
    - Do not praise unnecessarily
    - Think like a recruiter reviewing hundreds of resumes quickly
    - Keep every point within 1 short line

    Return STRICTLY in this format:

    ATS SCORE:
    (Realistic ATS score out of 100)

    KEY STRENGTHS:
    - strongest matching skills
    - strongest relevant experience
    - strongest relevant project/domain

    MISSING REQUIREMENTS:
    - important missing skill
    - important missing tool/framework
    - important missing experience

    HIRING CONCERNS:
    - practical recruiter concern
    - practical recruiter concern

    FINAL DECISION:
    (Hire / Consider / Reject)

    REASON:
    (1-line recruiter justification)

    Job Description:
    {query}

    Candidate Resume:
    {context}
    """

    response = llm.invoke(prompt)
    return {
        "feedback": response.content
    }
    
@app.post("/candidate-feedback")
def candidate_feedback(data: MatchRequest):

    prompt = f"""
    You are an expert AI career coach and ATS resume strategist.

    Your task is to help the candidate improve resume shortlisting chances for the given job role.

    Guidelines:
    - Speak directly to the candidate
    - Focus on actionable improvements
    - Avoid generic motivational language
    - Keep advice concise and practical
    - Prioritize ATS optimization and recruiter expectations
    - Keep every point within 1 short line
    - Suggest only high-impact improvements

    Return STRICTLY in this format:

    ATS SCORE:
    (score out of 100)

    YOUR STRONG POINTS:
    - strong matching skill
    - strong matching project
    - relevant experience

    YOU SHOULD IMPROVE:
    - missing technical skill
    - weak resume section
    - missing practical exposure

    IMPORTANT KEYWORDS TO ADD:
    - keyword
    - keyword
    - keyword

    RESUME IMPROVEMENT TIPS:
    - practical improvement
    - practical improvement

    FINAL CAREER ADVICE:
    (1-line realistic advice)

    Job Description:
    {data.jd_text}

    Resume:
    {data.resume_text}
    """

    response = llm.invoke(prompt)

    return {
        "feedback": response.content
    }
    
@app.get("/interview")
def generate_interview_questions(query:str):
    results=vector_store.similarity_search(query=query,k=1)
    context="\n\n".join([doc.page_content for doc in results])
    prompt=f"""
    You are a senior technical interviewer at a top software company.

    Generate the TOP 15 highest-priority interview questions the candidate must prepare for based on the resume and job description.

    Rules:
    - Prioritize real-world interview questions
    - Focus on the most likely questions asked in actual interviews
    - Include technical + HR + project questions
    - Keep answers concise and interview-ready
    - Answers must sound natural for speaking in interviews
    - Keep each answer within 1-2 lines maximum
    - Avoid textbook explanations

    Return format:

    1. Question

    Answer:
    (short practical interview answer)

    Job Description:
    {query}

    Candidate Resume:
    {context}
    """
    response=llm.invoke(prompt)
    return {"interview_questions":response.content}

@app.get("/recruiter-interview")
def recruiter_interview(query:str):
    prompt=f"""
    You are a senior engineering interviewer.

    Generate ONLY the TOP 10 highest-quality interview questions for evaluating candidates for this role.

    Guidelines:
    - Questions must be practical and realistic
    - Focus on technical depth and problem-solving
    - Include concise expected answers
    - Avoid beginner-level trivia questions
    - Keep answers within 1-2 lines
    - Mix technical and behavioral questions

    Return format:

    1. Question

    Expected Answer:
    (short interviewer expectation)

    Job Description:
    {query}
    """
    response=llm.invoke(prompt)
    return {
        "interview_questions":response.content
    }
    
@app.delete("/clear")
def clear_vector_db():
    global vector_store
    try:
        client.delete_collection("resumes")
    except:
        pass

    vector_store = Chroma(
        client=client,
        collection_name="resumes",
        embedding_function=embedding_model
    )
    return {
        "message":"Vector DB reset successful"
    }
    
    
if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8001)

