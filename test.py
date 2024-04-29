import json
from pprint import pprint

import requests
from fuzzywuzzy import fuzz

from parser import Parser
from claude import Claude
from elastic_search import get_resumes


def send_get_request(url):
    try:
        header = {"X-Api-Key": "b16ed8c7ea04eaf46f0a"}
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occured while getting JD {e}")


def compare_tools(applicant_tools, jd_tools, weightage):
    applicant_tools_set = set([tools.lower() for tools in applicant_tools])
    jd_tools_set = set([tools.lower() for tools in jd_tools])
    same_tools = applicant_tools_set.intersection(jd_tools_set)
    non_compliance_set = list(jd_tools_set - applicant_tools_set)
    compliance_set = list(same_tools)
    tool_to_remove = []
    if non_compliance_set != []:
        for tool in non_compliance_set:
            for app_tool in applicant_tools:
                if tool.lower() in app_tool.lower() or fuzz.partial_ratio(tool.lower(), app_tool.lower()) > 75:
                    tool_to_remove.append(tool)
                    compliance_set.append(tool)
                    break
    tool_to_remove = list(set(tool_to_remove))
    for tool in tool_to_remove:
        non_compliance_set.remove(tool)
    return {"obtained": len(compliance_set) * weightage['tools'] / len(jd_tools_set), "total": weightage['tools'],
            "required": jd_tools, "compliance": list(compliance_set), "non_compliance": list(non_compliance_set),
            "weightage": weightage['tools']}


def compare_location(applicant_location, city, country, weightage):
    compliance_set, non_compliance_set = [], []
    score = 0
    if applicant_location.get("country", "").lower() == country.lower():
        score = weightage['country']
        compliance_set.append(country)
    else:
        non_compliance_set.append(country)
    if applicant_location.get("city", "").lower() in city.lower():
        score += weightage['city']
        compliance_set.append(city)
    else:
        non_compliance_set.append(city)
    return {"obtained": score, "required": [city, country], "compliance": list(compliance_set),
            "non_compliance": list(non_compliance_set), "weightage": weightage['city'] + weightage['country'],
            "total": weightage['city'] + weightage['country']}


def compare_qualification(application_qualification, jd_qualification, claude, weightage):
    if (application_qualification.replace("Bachelor", "").replace("of", "").replace(" ",
                                                                                    "").lower() == jd_qualification.replace(
        "Bachelor", "").replace("of", "").replace(" ", "").lower()):
        return {"obtained": weightage['qualification'], "required": [jd_qualification],
                "compliance": [jd_qualification], "non_compliance": [jd_qualification],
                "weightage": weightage['qualification'], "total": weightage['qualification']}
    if application_qualification != "" and jd_qualification != "":
        parser = Parser()
        score_format = '{"score": ##}'
        score = claude.predict_score(f"""
        Job description requires following qualification {jd_qualification}. My CV have following {application_qualification}.
         Score qualification out of 2. return following <p>{score_format}</p>
        """)
        score = parser.get_tags(score)[0]
        score = json.loads(score)
        score = score.get("score", 0)
        compliance_set, non_compliance_set = [], []
        if score >= 0:
            compliance_set.append(jd_qualification)
        else:
            compliance_set.append(jd_qualification)
        return {"obtained": score * weightage['qualification'] / 2, "required": [jd_qualification],
                "compliance": compliance_set, "non_compliance": non_compliance_set,
                "weightage": weightage['qualification'], "total": weightage['qualification']}
    else:
        return {"obtained": 0, "required": [jd_qualification], "compliance": [], "non_compliance": [jd_qualification],
                "weightage": weightage['qualification'], "total": weightage['qualification']}


def compare_experience(application_experience, jd_experience, title, jd, skills, claude, weightage):
    parser = Parser()
    prompt = f"""
    Your task is to find out all relevant experience for {title}, with the following priority:
    1. Match the position title with "{title}" or similar relevant titles.
    2. If any one skill matches then company should be considered here are all skills {skills}.
    This is the job description: {jd}
    And here are all the companies: {application_experience}.
    You should output with <p>["###", "###"]</p> if any are suitable, else <p>[]</p>.
    """
    text = claude.predict_score(prompt)
    companies = json.loads(parser.get_tags(text)[0])
    experience = 0
    compliance_set, non_compliance_set = [], []
    for applicant in application_experience:
        if applicant.get("company", "") in companies:
            duration = applicant.get("duration", {})
            duration = duration.get("month", 0) + duration.get("year", 0) * 12
            experience += duration
            compliance_set.append(f"{applicant.get('company', '')} ({round(duration / 12, 2)} Years)")
        else:
            duration = applicant.get("duration", {})
            duration = duration.get("month", 0) + duration.get("year", 0) * 12
            non_compliance_set.append(f"{applicant.get('company', '')} ({round(duration / 12, 2)} Years)")
    return {"obtained": min(weightage['experience'], experience * weightage['experience'] / jd_experience),
            "required": [f"{round(jd_experience / 12, 2)} year of experience"], "compliance": compliance_set,
            "non_compliance": non_compliance_set, "weightage": weightage['experience'],
            "total": weightage['experience']}


def get_summary(data, claude, applicant_name):
    output_format = """{"skills": "---", "location":"---", "experience": "--", "education":"---"}"""
    text = f"""Here is my score break down, You will need to provide summary for each score breakdown in such a way so that it is understandable by human.
{data}
Here are details about every breakdown
skills:
percentage: Percentage obtained in skills
obtained: obtained score for matching skills
total: total score of skills
weightage: weightage of skills in total score percentage
required: required skills for job
compliance: matching skills
non-compliance: non matching skills
Experience:
percentage: Percentage obtained in experience
obtained: obtained score for all companies duration with relevant experience
total: total score of experience
weightage: weightage of experience in total score percentage
required: required experience for job
compliance: companies duration with relevant experience
non-compliance: all companies duration with non - relevant experience
Education:
percentage: Percentage obtained in education
obtained: obtained score for matching education
total: total score of education
weightage: weightage of education in total score percentage
required: required education for job
compliance: matching education
non-compliance: non matching education
Location:
percentage: Percentage obtained in Location
obtained: obtained score for matching Location
total: total score of Location
weightage: weightage of Location in total score percentage
required: required Location for job
compliance: matching Location
non-compliance: non matching Location
Here is required output
<p>{output_format}</p>
Constraint: output should be in json wrapped around p tag
Use applicant name where Necessary. Applicant name is
{applicant_name}. For instance The skill sections shows that {applicant_name} have ...
    """
    parser = Parser()
    summary = claude.predict_summary(text)
    summary = parser.get_tags(summary)[0]
    summary = json.loads(summary)
    data['skills']['summary'] = summary["skills"]
    data['experience']['summary'] = summary["experience"]
    data['education']['summary'] = summary["education"]
    data['location']['summary'] = summary["location"]


def get_scores(job_id, applicant_id):
    claude = Claude()
    job_data = send_get_request(f"https://dev-api.3cix.com/api/external/job-description/job-by-id/{job_id}")
    applicant_data = get_resumes(applicant_id)

    weightage = {"tools": 40, "country": 6, "city": 4, "qualification": 10, "experience": 40}
    if job_data['educationWeightage'] + job_data['experienceWeightage'] + job_data['locationWeightage'] + job_data[
        'skillsWeightage'] == 100:
        weightage['tool'] = job_data['skillsWeightage']
        weightage['country'] = job_data['locationWeightage'] / 2
        weightage['city'] = job_data['locationWeightage'] / 2
        weightage['qualification'] = job_data['educationWeightage']
        weightage['experience'] = job_data['experienceWeightage']

    applicant_tools = applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get(
        "other_skills", []) + applicant_data.get('similar_skills', [])
    skill_score = compare_tools(applicant_tools, job_data['toolsHandlingExperience'].split(','), weightage)  # 40 %

    education = ", ".join([edu.get("degree", "") for edu in applicant_data.get("json_education", [])])
    qualification_score = compare_qualification(education, job_data.get("qualification", ""), claude, weightage)
    if skill_score['obtained'] > 0:
        experience_score = compare_experience(applicant_data.get('working_experience', []),
                                              float(job_data.get('experience', '0')) * 12, job_data.get('jobTitle'),
                                              job_data.get('detailedJobDescription', ''),
                                              job_data.get('toolsHandlingExperience'), claude, weightage)  # 40 %
    else:
        experience_score = {"obtained": 0, "required": [f"{job_data.get('experience', '0')} year of experience"],
                            "compliance": [], "non_compliance": [], "weightage": weightage['experience'],
                            "total": weightage['experience']}
        for applicant in applicant_data.get('working_experience', []):
            duration = applicant.get("duration", {})
            duration = duration.get("month", 0) + duration.get("year", 0) * 12
            experience_score["non_compliance"].append(
                f"{applicant.get('company', '')} ({round(duration / 12, 2)} Years)")

    location_score = compare_location(applicant_data.get('json_location', {}), ", ".join(job_data.get("city")),
                                      job_data.get("location", ""), weightage)

    total_score = skill_score['obtained'] + qualification_score['obtained'] + experience_score['obtained'] + \
                  location_score['obtained']
    skill_score['percentage'] = round(skill_score['obtained'] * 100 / skill_score['total'], 2)
    experience_score['percentage'] = round(experience_score['obtained'] * 100 / experience_score['total'], 2)
    qualification_score['percentage'] = round(qualification_score['obtained'] * 100 / qualification_score['total'], 2)
    location_score['percentage'] = round(location_score['obtained'] * 100 / location_score['total'], 2)
    output = {"skills": skill_score, "experience": experience_score, "education": qualification_score,
              "location": location_score}
    get_summary(output, claude, applicant_data.get('name', ''))
    output["percentage"] = round(total_score, 2)
    pprint(output)
    return output


if __name__ == "__main__":
    applicant_ids = ["6e1f289c-5dd5-4487-9da4-712dfd7ae65a"]
    for applicant_id in applicant_ids:
        score = get_scores("0b47b95b-3004-4b13-a05c-124e2874dd29", applicant_id)
        pprint(score)
