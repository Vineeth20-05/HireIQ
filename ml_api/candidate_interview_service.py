# candidate_interview_service.py

import json
import re
from llm_config import llm

def generate_candidate_interview_questions(context,query):

    prompt=f"""
You are a Senior Software Engineering Interview Panel consisting of:

- Engineering Manager
- Technical Lead
- Senior Software Engineer
- Hiring Manager

Generate the 15 highest-priority interview questions the candidate is most likely to face based on BOTH the resume and job description.

Rules:

1. Generate EXACTLY 15 questions.

2. Questions must be tailored to:
- Candidate Resume
- Job Description
- Skills
- Projects
- Experience

3. Include a balanced mix of:
- Technical
- Coding
- Project
- Behavioral
- Debugging
- System Design

4. Questions should increase in difficulty.

5. Avoid textbook theory questions.

6. Focus on real interview scenarios.

7. Keep expected answers concise.

8. For Coding questions:

Return COMPLETE working code.

IMPORTANT:

Return the code exactly as it would appear in a source file.

DO NOT compress code.

DO NOT write code on a single line.

Every statement MUST be on its own line.

Use proper indentation.

Preserve all newlines.

Return code inside the JSON string using escaped newline characters (\n).

Example:

sample_code:

public ListNode reverseList(ListNode head){{

    ListNode prev = null;
    ListNode curr = head;

    while(curr != null){{

        ListNode next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;

    }}

    return prev;

}}

9. For non-coding questions:

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

Allowed Types:

- Coding
- Technical
- System Design
- Debugging
- Behavioral
- Project

Resume:
{context}

Job Description:
{query}
"""

    response=llm.invoke(prompt)

    print("RAW CANDIDATE INTERVIEW RESPONSE:")
    print(response.content)

    try:

        content=response.content.strip()
        content=content.replace("```json","").replace("```","").strip()

        match=re.search(r"\{[\s\S]*\}",content)

        if not match:
            print("NO JSON FOUND")
            return {"questions":[]}

        data=json.loads(match.group())

        for question in data.get("questions",[]):

            if question.get("sample_code"):
                question["sample_code"]=question["sample_code"].replace("\\n","\n")
                
            if question.get("type") != "Coding":
                question["sample_code"] = ""
                question["time_complexity"] = ""
                question["space_complexity"] = ""
        return{
            "questions":data.get("questions",[])
        }

    except Exception as e:

        print("CANDIDATE INTERVIEW ERROR:",e)
        print(response.content)

        return {
            "questions":[]
        }