
import spacy
from pprint import pprint


nlp = spacy.load("en_core_web_sm")

weightage = {
    'specific_keyword_jd_match':4,
    'basic_keyword_jd_match':2,
    'nlp_keyword_jd_match':4,
}
def compare_skills(applicant_tools, jd_tools):
    applicant_tools_set = set([tools.lower() for tools in applicant_tools])
    jd_tools_set = set([tools.lower() for tools in jd_tools])
    same_tools = applicant_tools_set.intersection(jd_tools_set)
    return {"total_score": weightage['specific_keyword_jd_match'], "compliance_set": list(same_tools),
            "non_compliance_set": list(jd_tools_set - applicant_tools_set),
            "obtained_score": len(same_tools) * weightage['specific_keyword_jd_match'] / len(jd_tools_set)}

def compare_basic_skills(applicant_tools, jd_tools):
    applicant_tools_set = set([tools.lower() for tools in applicant_tools])
    jd_tools_set = set([tools.lower() for tools in jd_tools])
    same_tools = applicant_tools_set.intersection(jd_tools_set)
    return {"total_score": weightage['basic_keyword_jd_match'], "compliance_set": list(same_tools),
            "non_compliance_set": list(jd_tools_set - applicant_tools_set),
            "obtained_score": len(same_tools) * weightage['basic_keyword_jd_match'] / len(jd_tools_set)}

def calculate_nlp_match_score(resume_doc, job_skills):
    nlp_matched_skills = []
    for skill in job_skills:
        skill_token = nlp(skill)
        similarity = max([skill_token.similarity(token) for token in resume_doc if token.has_vector])
        if similarity > 0.7:  # Set a similarity threshold
            nlp_matched_skills.append(skill)
    # return len(nlp_matched_skills) * nlp_weight/
    return {"total_score": weightage['nlp_keyword_jd_match'], "compliance_set": nlp_matched_skills,
            "non_compliance_set": "",
            "obtained_score": len(nlp_matched_skills) * weightage['nlp_keyword_jd_match'] / len(job_skills)}

def hybrid_skill_score_calculation(applicant_data,job_data):
    print("********Skill Score Calculation********")
    providedSkills = job_data['toolsHandlingExperience'].split(',')
    print("****applicant skills****")
    applicant_tools = (applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get("other_skills", []))
    compare_skills_result = compare_skills(applicant_tools, providedSkills)
    print(compare_skills_result)


    # basic keyword_skills matching
    detailedJobData = job_data.get("jobRequirements", {})
    print(detailedJobData)
    job_desc_doc = nlp(detailedJobData)
    job_skills = [token.text.lower() for token in job_desc_doc if token.pos_ == "NOUN"]
    print(job_skills)
    print(applicant_tools)
    job_skill_score = compare_basic_skills(applicant_tools, job_skills)
    print(job_skill_score)
    # pprint(applicant_data)

    total_experience = ""
    for experience in applicant_data['working_experience']:
        total_experience = total_experience  + ','.join(experience['responsibilities'])

    # print(total_experience)
    total_experience = nlp(total_experience)
    nlp_match_score = calculate_nlp_match_score(total_experience, job_skills)
    pprint(nlp_match_score)