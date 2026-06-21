# ml_api/talent_search_service.py

import json
import re
from llm_config import llm

def talent_search(query,candidates):

    prompt=f"""
You are a Principal Technical Recruiter and Talent Acquisition Lead.

Analyze all candidate resumes and identify the best candidates for the recruiter request.

Evaluation Criteria:
- Technical Skills Match
- Experience Relevance
- Project Relevance
- Technology Stack Alignment
- Domain Alignment

Rules:

1. Return ONLY the top 5 most relevant candidates.

2. Match Score Guidelines:

90-100 = Excellent Match
75-89 = Strong Match
60-74 = Good Match
0-59 = Weak Match

3. matched_skills:
- Maximum 10 skills
- Only skills relevant to recruiter query
- Only skills actually present in candidate resume

4. strengths:
- Maximum 3 concise recruiter observations

5. Never invent skills.

6. Never invent experience.

7. Return candidates sorted by match_score descending.

8. recommendation must follow score:

91-100 = Strong Hire
75-90 = Hire
50-74 = Consider
0-49 = Reject

9. Return ONLY valid JSON.

matched_skills MUST contain ONLY skills that:
1. Appear in recruiter query/JD
2. Appear in candidate resume

Do NOT include resume-only skills.

Example:

{{
    "top_candidates":[
        {{
            "candidate_name":"John Doe",
            "match_score":92,
            "matched_skills":["Python","FastAPI","AWS"],
            "strengths":[
                "Strong backend experience",
                "Relevant cloud expertise",
                "Production API development"
            ],
            "recommendation":"Strong Hire"
        }}
    ]
}}

Recruiter Query:
{query}

Candidate Data:
{candidates}
"""

    response=llm.invoke(prompt)

    print("RAW TALENT SEARCH:")
    print(response.content)

    try:

        match=re.search(r"\{.*\}",response.content,re.DOTALL)

        if not match:
            return {"top_candidates":[]}

        result=json.loads(match.group())

        for candidate in result.get("top_candidates",[]):

            score=int(candidate.get("match_score",0))

            if score>=91:
                candidate["recommendation"]="Strong Hire"

            elif score>=75:
                candidate["recommendation"]="Hire"

            elif score>=50:
                candidate["recommendation"]="Consider"

            else:
                candidate["recommendation"]="Reject"

        result["top_candidates"]=sorted(
            result.get("top_candidates",[]),
            key=lambda x:x.get("match_score",0),
            reverse=True
        )

        return result

    except Exception as e:

        print("TALENT SEARCH ERROR:",e)
        print(response.content)

        return {
            "top_candidates":[]
        }