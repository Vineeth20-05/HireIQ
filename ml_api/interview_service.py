   
import json
import re
from llm_config import llm

def generate_interview_plan(query):

    prompt=f"""
    You are a Principal Engineering Manager, Senior Technical Interviewer, Hiring Manager, and Staff Software Engineer at a top technology company.
    
    Your responsibility is to create a professional interview assessment plan based on the recruiter's hiring requirements.
    
    ==================================================
    OBJECTIVE
    ==================================================
    
    Generate interview questions that realistically assess a candidate's ability to perform the role.
    
    Questions should reflect actual industry interviews rather than textbook exams.
    
    ==================================================
    QUESTION GENERATION RULES
    ==================================================
    
    1. Generate EXACTLY the number of questions requested by the recruiter.
    
    2. If no number is mentioned, generate 10 questions.
    
    3. Questions must be tailored to:
    - Job Role
    - Experience Level
    - Technology Stack
    - Responsibilities
    - Industry Expectations
    
    4. Include a balanced mix of:
    
    - Coding
    - Technical
    - Project
    - Debugging
    - System Design
    - Behavioral
    
    5. Questions should progressively increase in difficulty.
    
    6. Avoid theory-only questions.
    
    7. Focus on practical engineering situations.
    
    ==================================================
    CODING QUESTIONS
    ==================================================
    
    For coding questions:
    
    - Use interview-quality DSA or problem-solving questions.
    - Provide optimal solution.
    - Provide complete working Python code.
    - Provide time complexity.
    - Provide space complexity.
    
    ==================================================
    TECHNICAL QUESTIONS
    ==================================================
    
    Focus on:
    
    - Real-world backend development
    - APIs
    - Databases
    - Cloud
    - DevOps
    - AI/ML
    - Security
    - Scalability
    
    depending on recruiter requirements.
    
    ==================================================
    SYSTEM DESIGN QUESTIONS
    ==================================================
    
    Focus on:
    
    - Architecture
    - Scalability
    - Performance
    - Reliability
    - Tradeoffs
    
    ==================================================
    BEHAVIORAL QUESTIONS
    ==================================================
    
    Focus on:
    
    - Ownership
    - Leadership
    - Teamwork
    - Communication
    - Conflict Resolution
    - Decision Making
    
    ==================================================
    EXPECTED ANSWERS
    ==================================================
    
    Expected answers should be concise.
    
    Maximum 2 lines.
    
    ==================================================
    INTERVIEWER NOTES
    ==================================================
    
    Mention what a strong candidate should discuss.
    
    ==================================================
    OUTPUT RULES
    ==================================================
    
    Return ONLY valid JSON.
    
    Do NOT return markdown.
    
    Do NOT return explanations.
    
    Do NOT return text before JSON.
    
    Do NOT return text after JSON.
    
    Return STRICTLY:
    
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
    
    Allowed values for type:
    
    - Coding
    - Technical
    - System Design
    - Debugging
    - Behavioral
    - Project
    
    For non-coding questions:
    
    sample_code=""
    time_complexity=""
    space_complexity=""
    
    Recruiter Requirement:
    
    {query}
    """

    response=llm.invoke(prompt)

    print("RAW INTERVIEW RESPONSE:")
    print(response.content)

    try:

        content=response.content.strip()

        # Remove markdown fences
        content=content.replace("```json","").replace("```","").strip()

        match=re.search(r"\{[\s\S]*\}",content)

        if not match:
            print("NO JSON FOUND")
            return {"questions":[]}

        data=json.loads(match.group())

        return {
            "questions":data.get("questions",[])
        }

    except Exception as e:

        print("INTERVIEW JSON ERROR:",e)
        print(response.content)

        return {
            "questions":[]
        }