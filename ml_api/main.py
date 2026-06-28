from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os,re
import uvicorn
from chroma_utils import vector_store, client, embedding_model
from langchain_chroma import Chroma
import uuid
from llm_config import llm
from ats_service import generate_ats_feedback
from talent_search_service import talent_search
from interview_service import generate_interview_plan
from candidate_feedback_service import generate_candidate_feedback
from candidate_interview_service import generate_candidate_interview_questions

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

    docs = vector_store.similarity_search(query=query, k=20, filter={"user_id": user_id})
    print("DOCS FOUND:", len(docs))

    candidates, seen = [], set()
    for doc in docs:
        candidate_name = doc.metadata.get("candidate_name")
        if not candidate_name or candidate_name in seen: continue
        seen.add(candidate_name)
        candidates.append({"candidate_name": candidate_name, "resume": doc.page_content})

    print("UNIQUE CANDIDATES:", len(candidates))

    result = talent_search(query=query, candidates=candidates)
    print("TALENT SEARCH RESULT:", result)

    return result


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
    results=vector_store.similarity_search(query=query,k=5)
    context=""
    for doc in results:
        if doc.metadata.get("candidate_name")==candidate_name:
            context=doc.page_content
            break
    return generate_ats_feedback(context=context,query=query)
    
@app.post("/candidate-feedback")
def candidate_feedback(data: MatchRequest):
    return generate_candidate_feedback(
        resume_text=data.resume_text,
        jd_text=data.jd_text
    )
    
@app.get("/interview")
def generate_interview_questions(query:str):
    results=vector_store.similarity_search(
        query=query,
        k=1)
    if not results:
        return {"questions":[]}
    context="\n\n".join([doc.page_content for doc in results])
    return generate_candidate_interview_questions(
        context=context,
        query=query)

@app.get("/recruiter-interview")
def recruiter_interview(query:str):
    return generate_interview_plan(query)

    
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
   uvicorn.run("main:app", host="0.0.0.0", port=8001)

