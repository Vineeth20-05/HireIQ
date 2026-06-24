# ml_api/candidate_feedback_service.py

import re
from llm_config import llm


def generate_candidate_feedback(resume_text: str, jd_text: str):

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
    skill1, skill2, skill3

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

    EXPERIENCE_ALIGNMENT:
    Excellent / Good / Average / Weak

    PROJECT_QUALITY:
    Excellent / Good / Average / Weak

    HIRING_RECOMMENDATION:
    Strong Hire / Hire / Consider / Reject

    EXECUTIVE_SUMMARY:
    Maximum 2 lines.

    Job Description:
    {jd_text}

    Resume:
    {resume_text}
    """

    response = llm.invoke(prompt)

    content = response.content

    print("RAW RESPONSE:")
    print(content)

    try:

        ats_score = re.search(
            r"ATS_SCORE:\s*(\d+)",
            content
        )

        experience = re.search(
            r"EXPERIENCE_ALIGNMENT:\s*(.*)",
            content
        )

        project_quality = re.search(
            r"PROJECT_QUALITY:\s*(.*)",
            content
        )

        interview_readiness = re.search(
            r"INTERVIEW_READINESS:\s*(.*)",
            content
        )

        recommendation = re.search(
            r"HIRING_RECOMMENDATION:\s*(.*)",
            content
        )

        summary = re.search(
            r"EXECUTIVE_SUMMARY:\s*(.*)",
            content,
            re.DOTALL
        )

        matched_skills = []
        missing_skills = []
        ats_keywords = []
        strengths = []
        roadmap = []

        matched_match = re.search(
            r"MATCHED_SKILLS:(.*?)MISSING_SKILLS:",
            content,
            re.DOTALL
        )

        if matched_match:
            matched_skills = [
                skill.strip()
                for skill in matched_match.group(1).split(",")
                if skill.strip()
            ]

        missing_match = re.search(
            r"MISSING_SKILLS:(.*?)ATS_KEYWORDS_TO_ADD:",
            content,
            re.DOTALL
        )

        if missing_match:
            missing_skills = [
                skill.strip()
                for skill in missing_match.group(1).split(",")
                if skill.strip()
            ]

        keyword_match = re.search(
            r"ATS_KEYWORDS_TO_ADD:(.*?)RESUME_STRENGTHS:",
            content,
            re.DOTALL
        )

        if keyword_match:
            ats_keywords = [
                skill.strip()
                for skill in keyword_match.group(1).split(",")
                if skill.strip()
            ]

        strengths_match = re.search(
            r"RESUME_STRENGTHS:(.*?)IMPROVEMENT_ROADMAP:",
            content,
            re.DOTALL
        )

        if strengths_match:

            strengths = [
                line.replace("-", "").strip()
                for line in strengths_match.group(1).split("\n")
                if line.strip()
            ]

        roadmap_match = re.search(
            r"IMPROVEMENT_ROADMAP:(.*?)INTERVIEW_READINESS:",
            content,
            re.DOTALL
        )

        if roadmap_match:

            roadmap = [
                line.replace("-", "").strip()
                for line in roadmap_match.group(1).split("\n")
                if line.strip()
            ]

        data = {
            "ats_score":
                int(ats_score.group(1))
                if ats_score else 0,

            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            "ats_keywords":
                ats_keywords,

            "strengths":
                strengths,

            "roadmap":
                roadmap,

            "interview_readiness":
                interview_readiness.group(1).strip()
                if interview_readiness else "Unknown",

            "experience_alignment":
                experience.group(1).strip()
                if experience else "Unknown",

            "project_quality":
                project_quality.group(1).strip()
                if project_quality else "Unknown",

            "recommendation":
                recommendation.group(1).strip()
                if recommendation else "Unknown",

            "summary":
                summary.group(1).strip()
                if summary else ""
        }

        print("CANDIDATE FEEDBACK DATA:")
        print(data)

        return data

    except Exception as e:

        print("CANDIDATE FEEDBACK ERROR:", e)

        return {
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "ats_keywords": [],
            "strengths": [],
            "roadmap": [],
            "interview_readiness": "Unknown",
            "experience_alignment": "Unknown",
            "project_quality": "Unknown",
            "recommendation": "Unknown",
            "summary": ""
        }