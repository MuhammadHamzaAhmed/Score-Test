import json
from pprint import pprint

import requests
from fuzzywuzzy import fuzz

from claude import Claude
from parser import Parser
from elastic_search import get_resumes
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_lg")
def send_get_request(url):
    try:
        header = {"X-Api-Key": "b16ed8c7ea04eaf46f0a"}
        response = requests.get(url, headers=header)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occured while getting JD {e}")


weightage = {"tools": 40, "country": 6, "city": 4, "qualification": 10, "experience": 40}


def compare_tools(applicant_tools, jd_tools):
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
    return {"total_score": weightage['tools'], "compliance_set": compliance_set,
            "non_compliance_set": non_compliance_set,
            "obtained_score": len(compliance_set) * weightage['tools'] / len(jd_tools_set)}


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



def preprocess_text(text):
    # Tokenize the text and remove stopwords and punctuation
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)

def calculate_similarity(description1, description2):
    print("---_Reaching Here")

    processed_desc1 = preprocess_text(description1)
    processed_desc2 = preprocess_text(description2)

    print(processed_desc1)
    print(processed_desc2)

    # Process the input descriptions
    doc1 = nlp(processed_desc1)
    doc2 = nlp(processed_desc2)

    # # Compute similarity between the processed descriptions
    # similarity_score = doc1.similarity(doc2)

    vectorizer = TfidfVectorizer()

    # Fit and transform the preprocessed descriptions
    tfidf_matrix = vectorizer.fit_transform([processed_desc1, processed_desc2])

    # Compute cosine similarity between the TF-IDF vectors
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    pprint(similarity_score)
    return similarity_score

def compare_experience(application_experience, jd_experience, title, jd, skills, claude):

    # Making sure that all companies that the applicant has worked on are really relevant
    for applicant in application_experience:
        print("----applicant---")
        print(applicant)
        print("----Similarity-----")
        print("----JD----")
        print(jd)
        print("---CompanyName---")
        print(applicant.get("company"))
        print('-----responsibilities_-----')
        print(' '.join(applicant.get('responsibilities')))
        k=calculate_similarity(jd,' '.join(applicant.get('responsibilities','')))
        print(k)

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

    print("----Company Name gathered from claude----")
    print(companies)



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
            applicant_data.get("tools", []) + applicant_data.get("skills", []) + applicant_data.get("other_skills",[]) + applicant_data.get('similar_skills', []))
    skill_score = compare_tools(applicant_tools, job_data['toolsHandlingExperience'].split(','))  # 40 %
    skill_score_weightage = skill_score['obtained_score'] * 40 / skill_score["total_score"]

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
    total_score = skill_score_weightage + qualification_score_weight + experience_score[
        'obtained_score'] + location_score_weight
    return {"percentage": round(total_score, 2), "skill_score": skill_score, "qualification_score": qualification_score,
            "experience_score": experience_score, "location_score": location_score, }


if __name__ == "__main__":
    applicant_ids = ["26b1211f-bb88-4f7f-a66c-5be2c5f3795d"]
    for applicant_id in applicant_ids:
        score = get_scores("0b47b95b-3004-4b13-a05c-124e2874dd29", applicant_id)
        pprint(score)
