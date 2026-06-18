import json
from llm_config import llm

def generate_interview_plan(query):

    prompt=f"""
    You are a Principal Engineering Interviewer, Engineering Manager, Technical Lead, and Hiring Manager responsible for designing interview assessments for top technology companies.

    Analyze the recruiter's hiring requirement and create a professional interview plan.

    Rules:

    1. Generate EXACTLY 10 questions unless recruiter explicitly requests another number.

    2. Questions must align with:
    - Job role
    - Seniority level
    - Required technologies
    - Industry expectations

    3. Include a balanced mix of:
    - Technical Questions
    - Coding Questions
    - Project-Based Questions
    - Debugging Questions
    - System Design Questions
    - Behavioral Questions

    4. Focus on real-world engineering scenarios.

    5. Avoid textbook definitions.

    6. Questions should progressively increase in difficulty.

    7. Expected answers should be concise and practical.

    8. Interviewer notes should mention what a strong candidate should discuss.

    9. If the question is a coding question:
    - Provide optimal code solution
    - Provide time complexity
    - Provide space complexity

    10. If the question is NOT a coding question:
    - sample_code = ""
    - time_complexity = ""
    - space_complexity = ""

    Return ONLY valid JSON.

    {{
    "questions":[
        {{
        "question":"",
        "type":"",
        "skill":"",
        "difficulty":"",
        "expected_answer":"",
        "sample_code":"",
        "time_complexity":"",
        "space_complexity":"",
        "interviewer_note":""
        }}
    ]
    }}

    Question Type must be one of:
    - Coding
    - Technical
    - System Design
    - Debugging
    - Behavioral
    - Project

    Examples:

    Coding Question:

    {{
    "question":"Find Two Sum",
    "type":"Coding",
    "skill":"Arrays",
    "difficulty":"Easy",
    "expected_answer":"Use hashmap for O(n) lookup",
    "sample_code":"def twoSum(nums,target): pass",
    "time_complexity":"O(n)",
    "space_complexity":"O(n)",
    "interviewer_note":"Candidate should understand hashmaps"
    }}

    Technical Question:

    {{
    "question":"Explain FastAPI Dependency Injection",
    "type":"Technical",
    "skill":"FastAPI",
    "difficulty":"Medium",
    "expected_answer":"Reusable dependency functions improve maintainability",
    "sample_code":"",
    "time_complexity":"",
    "space_complexity":"",
    "interviewer_note":"Look for practical production examples"
    }}

    Recruiter Requirement:

    {query}
    """

    response=llm.invoke(prompt)

    try:
        return json.loads(response.content)

    except Exception as e:
        print("INTERVIEW JSON ERROR:",e)
        print(response.content)

        return {
            "questions":[]
        }