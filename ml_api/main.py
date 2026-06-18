from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os,re
import uvicorn
from chroma_utils import vector_store, client, embedding_model
from langchain_chroma import Chroma
import uuid
from langgraph_workflow import workflow
from llm_config import llm
from ats_service import generate_ats_feedback

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
def rank_candidates(jd:str,user_id: str,limit: int = 5):
    limit = max(1, min(limit, 100))
    results = vector_store.similarity_search_with_score(jd, k=limit, filter={"user_id": user_id})
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
    results=vector_store.similarity_search(
        query=query,
        k=5)
    context=""
    for doc in results:
        if doc.metadata.get("candidate_name")==candidate_name:
            context=doc.page_content
            break
    return generate_ats_feedback(
        context=context,
        query=query
    )

    
@app.post("/candidate-feedback")
def candidate_feedback(data: MatchRequest):
    prompt = f"""
    You are a Senior Career Strategist, ATS Consultant, and Hiring Coach.

    Your objective is to maximize the candidate's interview conversion rate and ATS shortlisting probability.

    Evaluation Criteria:
    - ATS compatibility
    - Skill alignment
    - Missing requirements
    - Resume quality
    - Project relevance
    - Industry readiness

    Rules:
    - Focus on actionable improvements only
    - Avoid generic motivation
    - Think like both a recruiter and career advisor
    - Prioritize high-impact improvements
    - Every point should be concise and practical

    Return STRICTLY:

    ATS_SCORE: <number>

    MATCHED_SKILLS:
    skill1, skill2, skill3, skill4

    MISSING_SKILLS:
    skill1, skill2, skill3

    ATS_KEYWORDS_TO_ADD:
    keyword1, keyword2, keyword3

    RESUME_STRENGTHS:
    - point
    - point
    - point

    IMPROVEMENT_ROADMAP:
    - point
    - point
    - point

    INTERVIEW_READINESS:
    High / Medium / Low

    CAREER_RECOMMENDATION:
    Maximum 2 lines.

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
    prompt = f"""
    You are a Senior Software Engineering Interview Panel consisting of:

    - Engineering Manager
    - Technical Lead
    - Senior Software Engineer
    - Hiring Manager

    Generate the 15 highest-priority interview questions the candidate is most likely to face based on BOTH the resume and job description.

    Guidelines:
    - Prioritize actual interview questions used in industry
    - Include project-based questions
    - Include technical questions
    - Include behavioral questions
    - Include architecture questions when applicable
    - Progress from moderate to advanced difficulty
    - Avoid textbook theory questions
    - Answers should sound natural when spoken
    - Keep answers within 1-2 lines

    Return STRICTLY:

    QUESTION:
    (question)

    WHY_INTERVIEWER_ASKS:
    (one short line)

    MODEL_ANSWER:
    (1-2 lines)

    Resume:
    {context}

    Job Description:
    {query}
    """
    response=llm.invoke(prompt)
    return {"interview_questions":response.content}

@app.get("/recruiter-interview")
def recruiter_interview(query: str):
    prompt = f"""
    You are a Principal Engineering Interviewer responsible for creating interview assessments for top technology companies.

    Analyze the recruiter's request and generate a professional interview evaluation set.

    Rules:

    1. If recruiter specifies a number, generate EXACTLY that many questions.

    2. If no number is specified, generate 10 questions.

    3. Questions must align with:
    - Job role
    - Seniority level
    - Required technologies
    - Industry expectations

    4. For coding assessments:
    - Generate interview-grade problems
    - Provide optimal solution
    - Include complete working code
    - Include time complexity
    - Include space complexity
    - Include interviewer evaluation points

    5. For technical interviews:
    - Focus on practical engineering scenarios
    - Include debugging questions
    - Include architecture questions
    - Include scalability questions where relevant

    6. For behavioral interviews:
    - Focus on ownership
    - Leadership
    - Conflict resolution
    - Stakeholder communication
    - Decision making

    Return STRICTLY:

    QUESTION:
    (question)

    SKILL_EVALUATED:
    (skill being tested)

    EXPECTED_ANSWER:
    (1-2 lines)

    INTERVIEWER_NOTE:
    (what a strong candidate should mention)

    Recruiter Request:
    {query}
    """
    response = llm.invoke(prompt)
    return {
        "interview_questions": response.content
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
    
@app.delete("/clear-user")
def clear_user_vectors(user_id: str):
    results = vector_store.get(
        where={
            "user_id": user_id
        }
    )
    if results["ids"]:
        vector_store.delete(
            ids=results["ids"]
        )
    return {
        "message": "User vectors deleted"
    }


if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8001)

