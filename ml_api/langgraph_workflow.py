from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from chroma_utils import vector_store
from llm_config import llm


class HiringState(TypedDict):
    query: str
    user_id: str
    retrieved_resumes: str
    analysis: str
    final_response: str


def retrieve_resumes(state: HiringState):
    results = vector_store.similarity_search(query=state["query"],k=3,filter={"user_id":state["user_id"]})
    context = "\n\n".join([doc.page_content[:3000] for doc in results])
    return {"retrieved_resumes": context}


def analyze_candidates(state: HiringState):
    prompt = ChatPromptTemplate.from_template("""
    You are a senior technical recruiter.
    Analyze the resumes against the recruiter query.
    Focus on:
    - strongest candidate
    - relevant skills
    - technical strengths
    - hiring concerns
    Keep response concise and recruiter-focused.

    Recruiter Query:
    {query}

    Resume Context:
    {retrieved_resumes}
    """)
    chain = prompt | llm
    response = chain.invoke({
        "query": state["query"],
        "retrieved_resumes": state["retrieved_resumes"]
    })
    return {"analysis": response.content}


def generate_final_response(state: HiringState):
    prompt = ChatPromptTemplate.from_template("""
    You are a senior hiring manager.
    Based on the candidate analysis, generate a final hiring recommendation.
    Return STRICTLY:

    BEST CANDIDATE:
    name

    HIRING DECISION:
    Hire / Consider / Reject

    FINAL REASON:
    short recruiter justification

    Candidate Analysis:
    {analysis}
    """)
    chain = prompt | llm
    response = chain.invoke({"analysis": state["analysis"]})
    return {"final_response": response.content}


builder = StateGraph(HiringState)
builder.add_node("retrieve_resumes", retrieve_resumes)
builder.add_node("analyze_candidates", analyze_candidates)
builder.add_node("generate_final_response", generate_final_response)
builder.add_edge(START, "retrieve_resumes")
builder.add_edge("retrieve_resumes", "analyze_candidates")
builder.add_edge("analyze_candidates", "generate_final_response")
builder.add_edge("generate_final_response", END)

workflow = builder.compile()
