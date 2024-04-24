import json
from pprint import pprint

import requests

from claude import Claude
from elastic_search import get_resumes
from parser import Parser
from Nova import CompleteDictionary
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
    if (application_qualification.replace("Bachelor", "").replace("of", "").replace(" ", "").lower()
            == jd_qualification.replace("Bachelor", "").replace("of", "").replace(" ", "").lower()):
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


def compare_experience(application_experience, jd_experience):
    application_experience_in_month = application_experience.get("year", 0) * 12 + application_experience.get("month",                                                                                                               0)
    return min(weightage['experience'], application_experience_in_month * weightage['experience'] / jd_experience)


def display_required(applicant_data, job_data):
    applicant = {
        "tools": applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get("other_skills",
                                                                                                         []),
        "location": applicant_data.get('json_location', {}), "qualification": applicant_data.get('json_education', {}),
        "total_experience": applicant_data.get('total_experience', {}), }

    job_data = {"tools": job_data.get("toolsHandlingExperience", "").split(","),
        "location": {"city": job_data.get("city")[0], "country": job_data.get("location", "")},
        "qualification": job_data.get("qualification", ""), "total_experience": job_data.get("experience", ""), }
    print("======================Started========================")
    print("======================Applicant======================")
    pprint(applicant)
    print("======================JD=============================")
    pprint(job_data)

def get_scores(job_id, applicant_id):
    job_data = send_get_request(f"https://dev-api.3cix.com/api/external/job-description/job-by-id/{job_id}")
    print("-----------------RAW JOB DESCRIPTION----------------------")
    print(job_data)
    applicant_data = get_resumes(applicant_id)
    display_required(applicant_data, job_data)
    hybrid_skill_score_calculation(applicant_data, job_data)
    # print("======================Score=============================")
    # applicant_tools = applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get(
    #     "other_skills", [])
    # tool_score = compare_tools(applicant_tools, job_data.get("toolsHandlingExperience", "").split(","))
    # location_score = compare_location(applicant_data.get('json_location', {}), job_data.get("city")[0],
    #                                   job_data.get("location", ""))
    # education = ", ".join([edu.get("degree", "") for edu in applicant_data.get("json_education", [])])
    # qualification_score = compare_qualification(education, job_data.get("qualification", ""))
    # experience_score = compare_experience(applicant_data.get('total_experience', {}),
    #                                       float(job_data.get('experience', 0)) * 12)
    # obtained_score = sum(
    #     [tool_score['obtained_score'], location_score['obtained_score'], qualification_score['obtained_score'],
    #      experience_score])
    # return {"total_score": sum(weightage.values()), "tools_score": tool_score, "location_score": location_score,
    #         "qualification_score": qualification_score, "experience_score": experience_score,
    #         "obtained_score": obtained_score, "percentage": 100 * obtained_score / sum(weightage.values())}
    return "Score Completed"


# def get_scores(job_id, applicant_id):
#     job_data = send_get_request(f"https://dev-api.3cix.com/api/external/job-description/job-by-id/{job_id}")
#     applicant_data = get_resumes(applicant_id)
#     display_required(applicant_data, job_data)
#     print("======================Score=============================")
#     applicant_tools = applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get(
#         "other_skills", [])
#     tool_score = compare_tools(applicant_tools, job_data.get("toolsHandlingExperience", "").split(","))
#     location_score = compare_location(applicant_data.get('json_location', {}), job_data.get("city")[0],
#                                       job_data.get("location", ""))
#     education = ", ".join([edu.get("degree", "") for edu in applicant_data.get("json_education", [])])
#     qualification_score = compare_qualification(education, job_data.get("qualification", ""))
#     experience_score = compare_experience(applicant_data.get('total_experience', {}),
#                                           float(job_data.get('experience', 0)) * 12)
#     obtained_score = sum(
#         [tool_score['obtained_score'], location_score['obtained_score'], qualification_score['obtained_score'],
#          experience_score])
#     return {"total_score": sum(weightage.values()), "tools_score": tool_score, "location_score": location_score,
#             "qualification_score": qualification_score, "experience_score": experience_score,
#             "obtained_score": obtained_score, "percentage": 100 * obtained_score / sum(weightage.values())}


# applicant_ids = ['b9c83433-0400-47cd-85a2-646630a52ebd', 'c6a7f188-6c0a-443b-92a3-da0c46a0dca1',
# 'bc9f9a4c-2286-4ee6-a7f3-16b0c88c98f9', 'cb49741b-afe5-40d0-99f7-8814c58a5aa0',
# 'fdfaf9e1-4864-4000-a5f8-b69d35843a21']
applicant_ids = ['26b1211f-bb88-4f7f-a66c-5be2c5f3795d']
for applicant_id in applicant_ids:
    score = get_scores("d252aff3-3bc4-44df-be9e-e165a272d36a", applicant_id)
    pprint(score)


    # print(round(score['percentage'], 2))
    # print("======================Finish=============================")
    # pprint(json.loads(CompleteDictionary("d252aff3-3bc4-44df-be9e-e165a272d36a", applicant_ids)[0]))
    # print("======================Finish=============================\n\n")
