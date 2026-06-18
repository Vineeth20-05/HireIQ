# ml_api/talent_search_service.py

import json
from llm_config import llm

def talent_search(query, candidates):

    prompt=f"""
    You are an AI Recruiting Consultant.

    Analyze all candidates and identify the best matches.

    Return ONLY valid JSON.

    {{
        "top_candidates":[
            {{
                "candidate_name":"",
                "match_score":0,
                "matched_skills":[],
                "strengths":[],
                "recommendation":""
            }}
        ]
    }}

    Recruiter Query:
    {query}

    Candidate Data:
    {candidates}
    """

    response=llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        return {
            "top_candidates":[]
        }