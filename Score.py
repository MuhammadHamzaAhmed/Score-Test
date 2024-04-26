import json
from pprint import pprint

import requests

from claude import Claude
from elastic_search import get_resumes
from parser import Parser
from skills_scoring import (hybrid_skill_score_calculation)


def send_get_request(url):
    try:
        header = {"X-Api-Key": "b16ed8c7ea04eaf46f0a"}
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occured while getting JD {e}")


weightage = {"tools": 5, "country": 3, "city": 2, "qualification": 2, "experience": 5}


def compare_tools(applicant_tools, jd_tools):
    applicant_tools_set = set([tools.lower() for tools in applicant_tools])
    jd_tools_set = set([tools.lower() for tools in jd_tools])
    same_tools = applicant_tools_set.intersection(jd_tools_set)
    return {"total_score": weightage['tools'], "compliance_set": list(same_tools),
            "non_compliance_set": list(jd_tools_set - applicant_tools_set),
            "obtained_score": len(same_tools) * weightage['tools'] / len(jd_tools_set)}


def compare_location(applicant_location, city, country):
    compliance_set, non_compliance_set = [], []
    score = 0
    if applicant_location.get("country", "").lower() == country.lower():
        score = 3
        compliance_set.append(country)
    else:
        non_compliance_set.append(country)
    if applicant_location.get("city", "").lower() == city.lower():
        score += 2
        compliance_set.append(city)
    else:
        non_compliance_set.append(city)
    return {"total_score": weightage['city'] + weightage['country'], "compliance_set": compliance_set,
            "non_compliance_set": non_compliance_set, "obtained_score": score}


def compare_qualification(application_qualification, jd_qualification):
    if (application_qualification.replace("Bachelor", "").replace("of", "").replace(" ",
                                                                                    "").lower() == jd_qualification.replace(
        "Bachelor", "").replace("of", "").replace(" ", "").lower()):
        return {"total_score": weightage['qualification'], "compliance_set": [jd_qualification],
                "non_compliance_set": [], "obtained_score": 2}
    if application_qualification != "" and jd_qualification != "":
        claude = Claude()
        parser = Parser()
        score_format = '{"score": ##}'
        score = claude.predict_text(f"""
        Job description requires following qualification {jd_qualification}. My CV have following {application_qualification}.
         Score qualification out of 2. return following <p>{score_format}</p>
        """)
        score = parser.get_tags(score)[0]
        score = json.loads(score)
        score = score.get("score", 0)
        return {"total_score": weightage['qualification'], "compliance_set": [jd_qualification if score > 0 else ""],
                "non_compliance_set": [jd_qualification if score == 0 else ""], "obtained_score": score}
    else:
        return {"total_score": weightage['qualification'], "compliance_set": [],
                "non_compliance_set": [jd_qualification], "obtained_score": 0}


def compare_experience(application_experience, jd_experience, title, jd, skills, claude):
    parser = Parser()
    prompt = f"""
I need a {title} to list all company names that are suitable for this job. You will disregard all companies that are irrelevant. Please ensure that exact matches are considered; for instance, testing experience cannot be equated with development experience. If all companies are irrelevant, there's no need to list any.
Here's the job description to give you an idea of what is required: {jd}.
Below are the required skills: {skills}.
And here are all the companies: {application_experience}.
You should output with <p>["###", "###"]</p> if any are suitable, else <p>[]</p>.

Constraints: You should include only those companies that have following skills {skills}.
    """
    text = claude.predict_text(prompt)
    companies = json.loads(parser.get_tags(text)[0])
    experience = 0
    compliance_set, non_compliance_set = [], []
    for applicant in application_experience:
        if applicant.get("company", "") in companies:
            duration = applicant.get("duration", {})
            experience += duration.get("month", 0) + duration.get("year", 0) * 12
            compliance_set.append(applicant.get("company", ""))
        else:
            non_compliance_set.append(applicant.get("company", ""))
    return {"total_score": 40, "obtained_score": min(40, experience * 40 / jd_experience),
            "compliance_set": compliance_set, "non_compliance_set": non_compliance_set}


def get_scores(job_id, applicant_id):
    job_data = send_get_request(f"https://dev-api.3cix.com/api/external/job-description/job-by-id/{job_id}")
    applicant_data = get_resumes(applicant_id)
    skill_score = hybrid_skill_score_calculation(applicant_data, job_data)  # 40 %

    education = ", ".join([edu.get("degree", "") for edu in applicant_data.get("json_education", [])])
    qualification_score = compare_qualification(education, job_data.get("qualification", ""))
    qualification_score_weight = qualification_score['obtained_score'] * 10 / qualification_score['total_score']  # 10 %

    experience_score = compare_experience(applicant_data.get('working_experience', []),
                                          float(job_data.get('experience', 0)) * 12, job_data.get('jobTitle'),
                                          job_data.get('detailedJobDescription', ''),
                                          job_data.get('toolsHandlingExperience'))  # 40 %

    location_score = compare_location(applicant_data.get('json_location', {}), job_data.get("city")[0],
                                      job_data.get("location", ""))
    location_score_weight = location_score['obtained_score'] * 10 / location_score['total_score']
    total_score = skill_score['obtained_score'] + qualification_score_weight + experience_score[
        'obtained_score'] + location_score_weight
    return {
        "total_score": total_score,
        "skill_score": skill_score,
        "qualification_score": qualification_score,
        "experience_score": experience_score,
        "location_score": location_score,
    }


if __name__ == "__main__":
    applicant_ids = ['b9c83433-0400-47cd-85a2-646630a52ebd', "7e97c216-b658-4dce-a0cb-09184e8c355a",
                     "22c44cca-8075-4cdf-8c69-12030efb0c18"]
    for applicant_id in applicant_ids:
        score = get_scores("917f9b5d-967a-49e8-9f18-199bbdb75631", applicant_id)
        pprint(score)
