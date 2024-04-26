import spacy

nlp = spacy.load("en_core_web_sm")

weightage = {'specific_keyword_jd_match': 4, 'basic_keyword_jd_match': 2, 'nlp_keyword_jd_match': 4, }


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


def hybrid_skill_score_calculation(applicant_data, job_data):
    providedSkills = job_data['toolsHandlingExperience'].split(',')
    applicant_tools = (
            applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get("other_skills", []))
    compare_skills_result = compare_skills(applicant_tools, providedSkills)

    detailedJobData = job_data.get("jobRequirements", {})
    job_desc_doc = nlp(detailedJobData)
    job_skills = [token.text.lower() for token in job_desc_doc if token.pos_ == "NOUN"]
    job_skill_score = compare_basic_skills(applicant_tools, job_skills)

    total_experience = ""
    for experience in applicant_data['working_experience']:
        total_experience = total_experience + ','.join(experience['responsibilities'])

    total_experience = nlp(total_experience)
    nlp_match_score = calculate_nlp_match_score(total_experience, job_skills)

    score = compare_skills_result['obtained_score'] * 80 / compare_skills_result['total_score']
    score += job_skill_score['obtained_score'] * 15 / job_skill_score['total_score']
    score += nlp_match_score['obtained_score'] * 5 / nlp_match_score['total_score']
    return score * 40 / 100
