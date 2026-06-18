import re
from llm_config import llm

VALID_ALIGNMENTS={"Excellent","Good","Average","Weak"}
VALID_RECOMMENDATIONS={"Strong Hire","Hire","Consider","Reject"}

def generate_ats_feedback(context:str,query:str)->dict:
    prompt=f"""
    You are an ATS Engine and Senior Technical Recruiter.

    Your task is to compare the Job Description and Resume.

    ==================================================
    STEP 1 - EXTRACT JD SKILLS
    ==================================================

    Extract ALL important technical skills from the Job Description.

    Include:
    - Programming Languages
    - Frameworks
    - Libraries
    - Databases
    - Cloud Platforms
    - DevOps Tools
    - Containers
    - AI/ML Tools
    - Data Engineering Tools
    - Testing Tools

    ==================================================
    STEP 2 - EXTRACT RESUME SKILLS
    ==================================================

    Extract ALL technical skills from the Resume.

    ==================================================
    STEP 3 - COMPARE
    ==================================================

    MATCHED_SKILLS =
    Skills present in BOTH JD and Resume.

    MISSING_SKILLS =
    Skills present in JD but NOT present in Resume.

    CRITICAL RULES:

    1. MATCHED_SKILLS must ONLY contain skills found in BOTH JD and Resume.

    2. MISSING_SKILLS must ONLY contain skills required by JD and absent from Resume.

    3. Never invent skills.

    4. Never infer skills.

    5. Never add explanation inside skill sections.

    6. If no missing skills:
    NONE

    ==================================================
    ATS SCORING
    ==================================================

    Calculate:

    Skill Match Percentage =
    (Matched Skills / Required JD Skills) × 100

    ATS score MUST follow:

    0-20% match:
    ATS_SCORE = 0-30

    21-40% match:
    ATS_SCORE = 31-50

    41-60% match:
    ATS_SCORE = 51-70

    61-80% match:
    ATS_SCORE = 71-85

    81-100% match:
    ATS_SCORE = 86-95

    Examples:

    Java Resume + Python JD:
    ATS_SCORE = 10-35

    Python Resume + Java JD:
    ATS_SCORE = 10-35

    Python Resume + AI Engineer JD:
    ATS_SCORE = depends on actual overlap

    Python + FastAPI + Docker + PostgreSQL Resume
    and
    Python Backend JD:
    ATS_SCORE = 75-90

    ==================================================
    EXPERIENCE_ALIGNMENT
    ==================================================

    Excellent
    Good
    Average
    Weak

    ==================================================
    PROJECT_QUALITY
    ==================================================

    Excellent
    Good
    Average
    Weak

    ==================================================
    HIRING_RECOMMENDATION
    ==================================================

    ATS_SCORE >= 90 -> Strong Hire
    ATS_SCORE >= 75 -> Hire
    ATS_SCORE >= 50 -> Consider
    ATS_SCORE < 50 -> Reject
    
    ==================================================
    SKILL PRIORITIZATION RULES
    ==================================================

    Only include MAJOR skills that materially impact hiring decisions.

    Priority Order:

    1. Programming Languages
    Examples:
    Python, Java, C#, Go, JavaScript, TypeScript

    2. Core Frameworks
    Examples:
    Django, FastAPI, Spring Boot, .NET, React, Angular

    3. Databases
    Examples:
    PostgreSQL, MySQL, MongoDB, Redis

    4. Cloud Platforms
    Examples:
    AWS, Azure, GCP

    5. Containers & Orchestration
    Examples:
    Docker, Kubernetes

    6. DevOps & CI/CD
    Examples:
    Jenkins, GitHub Actions, Terraform

    7. AI/ML Technologies
    Examples:
    TensorFlow, PyTorch, LangChain, RAG, Vector Databases

    8. Data Engineering Technologies
    Examples:
    Spark, Kafka, Airflow, Hadoop

    Do NOT include minor technologies such as:
    - Logging libraries
    - Utility libraries
    - Small plugins
    - IDEs
    - Editors
    - Office tools

    Examples:

    GOOD:
    Python, FastAPI, PostgreSQL, Docker, AWS

    BAD:
    Lombok, Log4j, VS Code, Eclipse, Notepad++, JUnit

    Return only skills that significantly impact hiring decisions.
    
    Maximum 20 matched skills.

    Maximum 20 missing skills.

    Prioritize only skills that materially impact hiring decisions.

    Ignore:
    - IDEs
    - Editors
    - Logging libraries
    - Utility libraries
    - Build tools unless explicitly required

    Examples:

    GOOD:
    Python, FastAPI, PostgreSQL, Docker, AWS, Kubernetes

    BAD:
    Log4j, Lombok, Eclipse, VS Code, Notepad++, JUnit

    ==================================================
    RETURN EXACTLY
    ==================================================

    ATS_SCORE: <number>

    MATCHED_SKILLS:
    skill1, skill2, skill3

    MISSING_SKILLS:
    skill1, skill2, skill3

    EXPERIENCE_ALIGNMENT:
    Excellent

    PROJECT_QUALITY:
    Excellent

    STRENGTHS:
    - point
    - point
    - point

    RISKS:
    - point
    - point

    HIRING_RECOMMENDATION:
    Hire

    EXECUTIVE_SUMMARY:
    Maximum 2 recruiter-style lines.

    ==================================================
    JOB DESCRIPTION
    ==================================================

    {query}

    ==================================================
    RESUME
    ==================================================

    {context}
    """

    response = llm.invoke(prompt)
    feedback = response.content
    print("RAW RESPONSE:")
    print(feedback)
    data = {
        "ats_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "experience_alignment": "",
        "project_quality": "",
        "strengths": [],
        "risks": [],
        "recommendation": "",
        "summary": ""
    }
    current_section = None
    for line in feedback.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("ATS_SCORE:"):
            match=re.search(r"\d+",line)
            if match: data["ats_score"]=int(match.group())

        elif line.startswith("MATCHED_SKILLS:"):
            skills=line.replace("MATCHED_SKILLS:","").strip()
            if skills:
                data["matched_skills"]=[
                    s.strip() for s in skills.split(",")
                    if s.strip()
                ]
            else:
                current_section="matched_skills"
                
        elif line.startswith("MISSING_SKILLS:"):
            skills=line.replace("MISSING_SKILLS:","").strip()

            if skills.upper()=="NONE":
                data["missing_skills"]=[]

            elif skills:
                data["missing_skills"]=[
                    s.strip() for s in skills.split(",")
                    if s.strip() and s.strip().lower() not in {"skill1","skill2","skill3"}
                ]
            else:
                current_section="missing_skills"
                
        elif line.startswith("EXPERIENCE_ALIGNMENT:"):
            value=line.replace("EXPERIENCE_ALIGNMENT:","").strip()
            if value in VALID_ALIGNMENTS: data["experience_alignment"]=value
            else: current_section="experience_alignment"

        elif line.startswith("PROJECT_QUALITY:"):
            value=line.replace("PROJECT_QUALITY:","").strip()
            if value in VALID_ALIGNMENTS: data["project_quality"]=value
            else: current_section="project_quality"

        elif line.startswith("HIRING_RECOMMENDATION:"):
            value=line.replace("HIRING_RECOMMENDATION:","").strip()
            if value in VALID_RECOMMENDATIONS: data["recommendation"]=value
            else: current_section="recommendation"

        elif line.startswith("STRENGTHS:"):
            current_section = "strengths"

        elif line.startswith("RISKS:"):
            current_section = "risks"

        elif line.startswith("EXECUTIVE_SUMMARY:"):
            summary = line.replace("EXECUTIVE_SUMMARY:","").strip()
            if summary:
                data["summary"] = summary
            else:
                current_section = "summary"
                
        else:
            if current_section=="matched_skills":
                data["matched_skills"].extend(
                    [s.strip() for s in line.split(",") if s.strip()]
                )
                
            elif current_section=="missing_skills":
                if line.upper()=="NONE":
                    data["missing_skills"]=[]
                else:
                    data["missing_skills"].extend(
                        [
                            s.strip() for s in line.split(",")
                            if s.strip()
                            and s.strip().lower() not in {"skill1","skill2","skill3"}
                        ]
                    )
                    
            elif current_section=="strengths" and line.startswith("-") and len(data["strengths"])<3:
                data["strengths"].append(line[1:].strip())

            elif current_section=="risks" and line.startswith("-") and len(data["risks"])<2:
                data["risks"].append(line[1:].strip())
            
            elif current_section=="experience_alignment":
                if line in VALID_ALIGNMENTS: data["experience_alignment"]=line

            elif current_section=="project_quality":
                if line in VALID_ALIGNMENTS: data["project_quality"]=line

            elif current_section=="recommendation":
                if line in VALID_RECOMMENDATIONS: data["recommendation"]=line

            elif current_section=="summary":
               data["summary"]=" ".join([data["summary"],line]).strip()
                
    data["experience_alignment"]=data["experience_alignment"] or "Average"
    data["project_quality"]=data["project_quality"] or "Average"
                        
    print("ATS DATA:", data)
    data["ats_score"]=max(0,min(100,data["ats_score"]))
    
    
    score=data["ats_score"]

    if score>=90:
        data["recommendation"]="Strong Hire"
    elif score>=75:
        data["recommendation"]="Hire"
    elif score>=50:
        data["recommendation"]="Consider"
    else:
        data["recommendation"]="Reject"

    if score<50 and data["experience_alignment"]=="Excellent":
        data["experience_alignment"]="Weak"

    if score<50 and data["project_quality"]=="Excellent":
        data["project_quality"]="Average"

    data["strengths"]=[s for s in data["strengths"] if s.lower()!="point"]
    data["risks"]=[r for r in data["risks"] if r.lower()!="point"]

    data["matched_skills"]=list(dict.fromkeys(data["matched_skills"]))[:20]
    data["missing_skills"]=list(dict.fromkeys(data["missing_skills"]))[:20]
    print("RAW RESPONSE:")
    print(feedback)
    return data
   
