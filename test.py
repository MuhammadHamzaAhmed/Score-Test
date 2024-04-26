import json

import requests

from claude import Claude
from parser import Parser
from pprint import pprint
from elastic_search import get_resumes

def send_get_request(url):
    try:
        header = {"X-Api-Key": "b16ed8c7ea04eaf46f0a"}
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occured while getting JD {e}")


weightage = {"tools": 5, "country": 3, "city": 2, "qualification": 2, "experience": 5}


def compare_tools(applicant_tools, jd_tools, projects, working_experience):
    applicant_tools_set = set([tools.lower() for tools in applicant_tools])
    jd_tools_set = set([tools.lower() for tools in jd_tools])
    same_tools = applicant_tools_set.intersection(jd_tools_set)
    non_compliance_set = list(jd_tools_set - applicant_tools_set)
    compliance_set = list(same_tools)
    if non_compliance_set != []:
        for tool in non_compliance_set:
            for app_tool in applicant_tools:
                if tool.lower() in app_tool.lower():
                    non_compliance_set.remove(tool)
                    compliance_set.append(tool)
    if non_compliance_set != []:
        for project in projects:
            for description in project.get("description", []):
                for skill in non_compliance_set:
                    if skill in description:
                        compliance_set.append(skill)
                        non_compliance_set.remove(skill)
                if not non_compliance_set == []:
                    break
            if not non_compliance_set == []:
                break
    if non_compliance_set != []:
        for experience in working_experience:
            for description in experience.get("responsibilities", []):
                for skill in non_compliance_set:
                    if skill in description:
                        compliance_set.append(skill)
                        non_compliance_set.remove(skill)
                if not non_compliance_set == []:
                    break
            if not non_compliance_set == []:
                break
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


def compare_qualification(application_qualification, jd_qualification, claude):
    if (application_qualification.replace("Bachelor", "").replace("of", "").replace(" ",
                                                                                    "").lower() == jd_qualification.replace(
        "Bachelor", "").replace("of", "").replace(" ", "").lower()):
        return {"total_score": weightage['qualification'], "compliance_set": [jd_qualification],
                "non_compliance_set": [], "obtained_score": 2}
    if application_qualification != "" and jd_qualification != "":
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
    claude = Claude("")
    job_data = send_get_request(f"https://dev-api.3cix.com/api/external/job-description/job-by-id/{job_id}")
    applicant_data = get_resumes(applicant_id)
    applicant_tools = (
            applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get("other_skills", []))
    skill_score = compare_tools(applicant_tools, job_data, applicant_data.get('json_projects'),
                                applicant_data.get('working_experience'))  # 40 %

    education = ", ".join([edu.get("degree", "") for edu in applicant_data.get("json_education", [])])
    qualification_score = compare_qualification(education, job_data.get("qualification", ""), claude)
    qualification_score_weight = qualification_score['obtained_score'] * 10 / qualification_score['total_score']  # 10 %
    if skill_score['obtained_score'] > 0:
        experience_score = compare_experience(applicant_data.get('working_experience', []),
                                              float(job_data.get('experience', 0)) * 12, job_data.get('jobTitle'),
                                              job_data.get('detailedJobDescription', ''),
                                              job_data.get('toolsHandlingExperience'), claude)  # 40 %
    else:
        experience_score = {"total_score": 40, "obtained_score": 0, "compliance_set": [],
                            "non_compliance_set": [work.get('company') for work in
                                                   applicant_data.get('working_experience', [])], }

    location_score = compare_location(applicant_data.get('json_location', {}), job_data.get("city")[0],
                                      job_data.get("location", ""))
    location_score_weight = location_score['obtained_score'] * 10 / location_score['total_score']
    total_score = skill_score['obtained_score'] + qualification_score_weight + experience_score[
        'obtained_score'] + location_score_weight
    return {"percentage": round(total_score, 2), "skill_score": skill_score, "qualification_score": qualification_score,
            "experience_score": experience_score, "location_score": location_score, }


if __name__ == "__main__":
    applicant_ids = ["774d94f7-4312-4454-9c7e-1dc090e52abe"]
    for applicant_id in applicant_ids:
        score = get_scores("afed150c-05fa-4ce6-ad81-730698c78e1c", applicant_id)
        pprint(score)
