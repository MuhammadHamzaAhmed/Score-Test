# %%
# Nova 5.0
import requests
import copy
import json

cachedStopWords = ['sometimes', "he'll", 'did', 'evaluate', 'consequence', 'around', 'easily', 'make', 'benefit',
                   'eventually', 'himself', 'besides', 'far', 'themselves', 'he', 'ever', 'everyone', 'fund', 'affect',
                   'major', 'enable', 'learn', 'advice', 'much', 'handle', 'must', 'has', 'for', 'continue', 'doesn',
                   'carry', 'detail', 'division', 'final', 'expand', 'going', 'equate', 'desire', 'two', 'both',
                   "c'mon", 'undoing', 'early', 'examine', 'isn', 'whoever', 'model', 'wasn', 'done', 'com', 'even',
                   'TRUE', 'then', 'am', 'my', 'goal', 'depend', 'would', 'any', 'was', 'were', 'energy', 'critical',
                   'mean', 'haven', 'avoid', 'eighty', 'kind', 'after', 'whereafter', 'too', 'game', 'conduct',
                   'containing', 'couldn', 'came', "shouldn't", 'been', 'near', 'awfully', 'amount', 'anything',
                   'believe', 'name', 'else', 'justify', 'level', 'outside', 'difference', 'expect', 'guess', 'herself',
                   'followed', 'expert', 'conclusion', 'alongside', 'format', 'will', 'grant', 'here', 'involve',
                   'most', "it'd", 'insight', 'intend', 'compare', 'became', 'plus', 'ex', "i'll", 'deal', 'knowledge',
                   'such', 'regardless', 'miss', 'mine', 'due', 'close', 'several', 'narrow', 'mustn', 'whatever',
                   'like', 'end', 'including', 'adequate', 'condition', 'consist', 'used', 'contain', 'things',
                   "should've", 'till', 'environment', 'change', 'aware', 'event', 'in', 'o', 'yours', 'at', 'many',
                   'rather', 'hadn', 'common', 'wherefore', 'inspire', 'last', 'doubt', 'that', 'may', 'someone',
                   'claim', 'don', 'more', 'contains', 'getting', 'demand', 'monitor', 'because', "we'd", 'former',
                   'look', 'upon', 'though', 'full', 'these', 'considering', 'appear', 'direct', 'is', 'light',
                   'accept', 'are', "you'll", 'century', 'welcome', 'could', 'how', 'a', 'somewhat', 'lift', 'denote',
                   'beyond', 'use', 'its', 'allow', 'it', 'thought', 'their', "i've", 'bear', 'kick', 'following',
                   'entirely', 'well', 'changes', 'down', "it'll", 'fewer', 'everywhere', 'contrast', 'date',
                   'generate', 'link', "he's", "can't", 'our', 'keen', 'those', 'grade', 'exhibit', 'ought', 'central',
                   'ma', 'doing', 'whose', 'when', 'emphasis', 'added', 'initial', "haven't", "that's", "she'll", 'as',
                   'except', 'being', 'wants', 'inside', 'fresh', 'whereas', 'formerly', 'need', 'suppose', 'soon',
                   'shouldn', 'discovery', 'load', 'seen', 'shan', 'only', "you're", 'assumption', "shan't",
                   'combination', 'y', 'five', 'this', 'yourselves', 'anywhere', 'evermore', 'jump', 'error', "c's",
                   'where', 'you', 'market', 'internal', 'thanks', 'amongst', "you've", 'one', 'wouldn', 'unto', 'sure',
                   'whether', 'next', 'leave', 'seemed', 'elsewhere', 'seems', 'really', 'estimate', "she's", 'lack',
                   'equal', 'theirs', 'off', 'belief', 'experience', 'fourteen', 'elaborate', 'whilst', 'everybody',
                   'balance', "there's", 'mix', 'few', 'consequently', 'dimension', "wasn't", 'good', 'way', 'hence',
                   'why', 'accordingly', 'or', 'explain', 'often', 'try', 'invest', 'whomever', 'on', "what's",
                   'chance', "i'm", 'below', 'complete', 'calculate', "hasn't", 'external', 'towards', 'corresponding',
                   'judge', 'come', 'between', 'distinguish', 'basis', 'does', 'lead', 'file', 'she', 'somebody',
                   'other', 'duty', 'i', 'mistake', 'again', 'derive', 'maintain', 'willing', 'etc', 'nor', 'and',
                   "couldn't", 'dare', "where's", 'leap', 'introduce', 'underneath', 'seem', 'control', "that'll",
                   'call', 'current', 'want', 'amid', 'per', "why's", 'above', 'just', 'anybody', 'something', 'eleven',
                   'approach', 'gone', 'determine', "isn't", "mustn't", "daren't", 'forth', 'encourage', "he'd",
                   'three', 'usually', 'out', 'later', 'goes', 'mind', 'neither', 'her', "they're", 'exclude', 'move',
                   'execute', 'can', 'since', "what'll", "we'll", 'exactly', 'assume', 'find', 'yet', 'whole', 'during',
                   'field', 'apart', 'manage', 'formulate', "here's", 'have', 'correspond', 'establish', 'nevertheless',
                   'face', 'using', 'to', 'function', 've', 'brief', 'sans', 'gets', 'always', 'given', 'example',
                   'design', 'therefore', 'by', 'enough', "they'll", 't', "mightn't", 'beforehand', 'quite', 'directly',
                   'extract', 'before', 'onto', 'feature', 'modify', 'lot', 'needn', 'discover', 'we', 'encounter',
                   'than', 'mention', 'll', 'very', 'comes', 'atop', 'become', 'seeming', 'negotiate', "let's",
                   'nowhere', 'maybe', 'somewhere', 'various', "who's", 'beside', 'under', 'certain', 'becoming',
                   'thence', 'care', 'factor', 'opposite', 'across', 'see', 'yes', 'argue', 'notwithstanding', 'hers',
                   'matter', 'but', 'zero', 'round', 'ground', 'distribute', "doesn't", 'without', 'nothing', 'confirm',
                   'minus', "it's", 'match', "weren't", 'his', 'if', 'them', 'should', 'figure', 'feedback', 'love',
                   'which', 'lately', 'live', 'however', 'all', 'force', 'your', 'against', 're', 'eighteen', 'fine',
                   'lose', 'behind', 'actual', 'measure', "we've", 'there', 'collect', 'oneself', 'conflict', 'know',
                   'comfort', 'within', 'throughout', "we're", 'clearly', 'frequent', 'perhaps', 'an', 'saw', 'great',
                   "aren't", 'prior', 'exceed', 'admit', 'constant', 'usual', 'belong', 'fill', 'ahead', 'grow',
                   'certainly', 'ourselves', 'focus', 'weren', 'anyone', 'still', 'no', 'form', 'forward', 'assess',
                   'future', 'listen', 'everything', 'motivate', 'now', 'along', 'little', 'evident', 'once', 'lay',
                   'lock', 'not', 'regarding', 'merge', 'further', 'toward', 'anyhow', 'contribute', 'constitute',
                   'same', 'altogether', 'catch', 'comment', 'past', 'lend', 'enhance', 'about', 'nobody', 'less',
                   'whereby', 'seeing', 'yourself', 'together', 'create', 'into', 'thus', 'unlike', 'amidst', 'better',
                   'join', "when's", 'do', 'while', 'aside', 'likewise', 'ain', 'employ', 'd', 'fifth', 'own', 'think',
                   'didn', 'unless', 'vs', 'myself', 'beneath', 'exact', 'so', 'twice', 'me', 'evolve', 'inquire',
                   'applied', 'got', 'consider', "she'd", 'until', 'either', 'difficult', 'instead', "they'd", 'some',
                   "i'd", 'enjoy', 'instance', 'concerning', 'trying', 'might', "ain't", 'us', 'downwards', 'itself',
                   'over', 'effect', 'fail', 'what', 'm', 'wherever', 'cause', 'another', 'efficient', 'ascertain',
                   'viz', 'self', 'who', "wouldn't", 'eight', 'supposing', 'laugh', 'thing', 'characteristic',
                   'respectively', 'whom', 'let', 'long', 'develop', 'able', 'get', 'first', 'fair', "that'd",
                   'despite', 'fall', 'won', "how's", 'element', 'limit', 'decide', 'they', 'thank', 'clear', 'genuine',
                   'never', 'marry', "needn't", 'follows', 'absolutely', 'from', 'up', 'lower', "they've", "hadn't",
                   'lest', 'happen', 'group', 'save', 'effort', 'be', 'concern', 'had', 'with', 'whenever',
                   'relatively', 'demonstrate', 'afford', "you'd", 'among', 'hasn', 'afterwards', 'interpret', 's',
                   "won't", 'every', 'general', 'mightn', 'through', "didn't", 'although', 'kiss', 'him', 'of',
                   'whichever', 'ours', 'the', 'cant', 'aren', 'becomes', 'frame', "don't", 'extend', 'cannot', 'shall',
                   'intervene', 'each', 'having', 'co', 'exception', 'none', 'said', 'friend']
from elasticsearch import Elasticsearch
import warnings

warnings.filterwarnings("ignore")
import re
from nltk.util import bigrams
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
import nltk
import numpy as np

# %% Defining Global Variables # Nova 5.0
ELASTIC_LINK = "https://elastic.3cix.com:443"
ELASTIC_PASS = "pK1k8c3RiBYxq943GY43e1U2"
ELASTIC_CLIENT = Elasticsearch(ELASTIC_LINK, basic_auth=("elastic", ELASTIC_PASS), verify_certs=False)
# %% Prod Variables
# Base_URL='api.3cix.com'
# api_key= '7e84b96482d66b834033'
# Index= 'search-resumes'
# %%
# A_ID_or_Detail = ['db567937-0afd-48d1-b5ea-43cb719a4cc4']

# JobUUID= 'afed150c-05fa-4ce6-ad81-730698c78e1c'
# %% Dev Variables
Base_URL = 'dev-api.3cix.com'
api_key = 'b16ed8c7ea04eaf46f0a'
Index = 'search-resumes-dev'
# %%
JOB_API = 'https://' + Base_URL + '/api/external/job-description/job-by-id/'
API_HEADER = {'x-api-key': api_key}
JobDataRequiredKeys = ['location', 'city', 'jobTitle', 'degreeName', 'experience', 'toolsHandlingExperience',
                       'qualification', 'certification', 'detailedJobDescription', 'jobRequirements', 'subIndustry',
                       'educationWeightage', 'experienceWeightage', 'locationWeightage', 'skillsWeightage']
CVDataRequiredKeys = ['certifications', 'designition', 'education', 'experience', 'jobExperience', 'location', 'skills',
                      'totalExperience', 'uniqueIdentifier', 'university', 'about_me', 'other_skills', 'publications',
                      'tools', 'json_certification', 'json_location', 'json_education', 'working_experience',
                      'json_projects', 'total_experience']


# %%

def CompleteDictionary(JobUUID, A_ID_or_Detail, isItIDs=True, IncludeMiscOrNot=False):
    JobData, RelevantIndustryVector = getAndCleanJobData(JobUUID)

    if isItIDs:
        AllApplicantsData = getApplicantData(A_ID_or_Detail)
        CompleteDictionary = []
        for A_Data in AllApplicantsData:
            compliance = OneToOneSimilarity(JobData, A_Data, RelevantIndustryVector, IncludeMiscOrNot)
            CompleteDictionary.append(compliance)

    else:
        CompleteDictionary = OneToOneSimilarity(JobData, json.loads(A_ID_or_Detail), RelevantIndustryVector,
                                                IncludeMiscOrNot)
    return CompleteDictionary


def OneToOneSimilarity(JobData, A_Data, RelevantIndustryVector, IncludeMiscOrNot):
    GlobalScore = {}
    J_LData = TransferIntoLiteral(JobData)  # populates Literal Data
    ######################## Compliance Check ####################
    GlobalScore['toolsHandlingExperience'] = getToolsCompliance(JobData, A_Data)
    GlobalScore['Location'] = getLocationCompliance(JobData, A_Data)
    GlobalScore['Experience'] = getExperienceCompliance(JobData, A_Data)
    GlobalScore['Qualification'] = getQualificationCompliance(J_LData, A_Data)
    if IncludeMiscOrNot:
        GlobalScore['Misc'] = getMiscCompliance(J_LData, A_Data)

    GlobalScore['uniqueIdentifier'] = A_Data['uniqueIdentifier']

    Classes = ['toolsHandlingExperience', 'Location', 'Qualification', 'Experience']
    if IncludeMiscOrNot:
        Classes.append('Misc')
    GrandTotalScore = 0
    GrandObtained = 0
    for c in Classes:
        GrandTotalScore += GlobalScore[c]['TotalScore']
        GrandObtained += GlobalScore[c]['ObtainedScore']

    GlobalScore['GrandTotalScore'] = GrandTotalScore
    GlobalScore['GrandObtainedScore'] = GrandObtained
    GlobalScore['Score(%)'] = GrandObtained / GrandTotalScore * 100
    # json.dumps(GlobalScore, default=list)
    return json.dumps(GlobalScore, default=list)


# %% computing uni/bi gram compliance
def getLocationCompliance(JobData, A_Data):
    JobCountry = copy.copy(JobData['location'])
    JobCity = copy.copy(JobData['city'])

    ApplicantLocation = []
    if 'city' in A_Data.keys():
        ApplicantLocation = [A_Data['city'], A_Data['state'], A_Data['country']]
    if 'location' in A_Data.keys():
        ApplicantLocation = A_Data['location']
    if 'json_location' in A_Data.keys():
        ApplicantLocation = [A_Data['json_location']['city'], A_Data['json_location']['state'],
                             A_Data['json_location']['country']]

    ApplicantLocation = list(set([x.lower() for x in ApplicantLocation]))

    ComplianceSet = set()
    NonComplianceSet = set()

    countryScore = 0

    if JobCountry in ApplicantLocation:
        ComplianceSet.add(JobCountry)
        countryScore = 3
    else:
        NonComplianceSet.add(JobCountry)

    CityScore = 0
    for i in JobCity:
        if i in ApplicantLocation:
            CityScore += 2
            ComplianceSet.add(i)
        else:
            NonComplianceSet.add(i)

    tempDict = {'TotalScore': 3 + (len(JobCity) * 2), 'ObtainedScore': CityScore + countryScore,
                'Detail': {'ComplianceSet': ComplianceSet, 'NonComplianceSet': NonComplianceSet}}

    return tempDict


def getExperienceCompliance(JobData, A_Data):
    ReqExperienceInMonths = int(JobData['experience']) * 12
    if 'total_experience' in A_Data.keys():
        AcqExperienceInMonts = A_Data["total_experience"]["year"] * 12 + A_Data["total_experience"]["month"]
    elif 'totalExperience' in A_Data.keys():
        AcqExperienceInMonts = A_Data["totalExperience"] * 12

    ObtainedScore = np.minimum(10, ((AcqExperienceInMonts * 10) / ReqExperienceInMonths))

    TempDict = {'Required': str(ReqExperienceInMonths) + ' months', 'Acquired': str(AcqExperienceInMonts) + ' months'}

    ExperienceDict = {'TotalScore': 10, 'ObtainedScore': ObtainedScore, 'Detail': TempDict}
    return ExperienceDict


def getQualificationCompliance(J_LData, A_Data):
    JKeys = ['qualification', 'degreeName', 'certification']
    if 'education' in A_Data.keys():
        AKeys = ['education', 'certifications']
    else:
        AKeys = ['json_education', 'json_certification']

    JValues = list({key: J_LData[key] for key in JKeys}.values())

    AValues = []
    for k in AKeys:
        try:
            AValues.append(A_Data[k])
        except:
            continue

    ComplianceSet = set()
    NonComplianceSet = set()
    pattern = r'[^a-zA-Z0-9\s]'

    refinedJValues = []
    for x in JValues:
        try:
            p = re.sub(pattern, '', x)
            p = CleanAndRemoveStopWords(p)
            p = p.split()
            p = list(set(p))
        except:
            continue
        refinedJValues.append(p)

    # p = [list(set(.split())) for x in JValues]
    JValuesRefined = []
    for x in refinedJValues:
        JValuesRefined += x
    JValuesRefined = list(set(['bachelor' if x == 'undergradbachelor' else x for x in JValuesRefined]))
    for i in JValuesRefined:
        if i in str(AValues).lower():
            ComplianceSet.add(i)
        else:
            NonComplianceSet.add(i)

    tempDict = {'TotalScore': len(ComplianceSet) + len(NonComplianceSet)}
    tempDict['ObtainedScore'] = len(ComplianceSet)
    tempDict['Detail'] = {'ComplianceSet': ComplianceSet, 'NonComplianceSet': NonComplianceSet}

    return tempDict


def getToolsCompliance(J_LData, A_Data):
    JKeys = ['toolsHandlingExperience']

    AKeys = ['designition', 'skills', 'experience', 'jobExperience', 'university', 'tools', 'skills', 'other_skills']
    if 'education' in A_Data.keys():
        AKeys.append('education')
        AKeys.append('certifications')
    elif 'json_education' in A_Data.keys():
        AKeys.append('json_education')
        AKeys.append('json_certification')

    JValues = list({key: J_LData[key] for key in JKeys}.values())

    AValues = []
    for k in AKeys:
        try:
            AValues.append(A_Data[k])
        except:
            continue

    JUniGram = JValues[0].split(',')

    ComplianceSet = set()
    NonComplianceSet = set()

    for i in JUniGram:
        if i in str(AValues).lower():
            ComplianceSet.add(i)
        else:
            NonComplianceSet.add(i)

    tempDict = {'TotalScore': 5}
    tempDict['ObtainedScore'] = np.minimum(5, (len(ComplianceSet) * 5) / (len(ComplianceSet) + len(NonComplianceSet)))
    tempDict['Detail'] = {'ComplianceSet': ComplianceSet, 'NonComplianceSet': NonComplianceSet}

    return tempDict


def getMiscCompliance(J_LData, A_Data):
    JKeys = ['detailedJobDescription', 'jobRequirements']
    JValues = list({key: J_LData[key] for key in JKeys}.values())

    AKeys = ['designition', 'skills', 'experience', 'jobExperience', 'university']
    if 'education' in A_Data.keys():
        AKeys.append('education')
        AKeys.append('certifications')
    elif 'json_education' in A_Data.keys():
        AKeys.append('json_education')
        AKeys.append('json_certification')

    AValues = []
    for k in AKeys:
        try:
            AValues.append(A_Data[k])
        except:
            continue

    ComplianceSet = set()
    NonComplianceSet = set()

    pattern = r'[^a-zA-Z0-9\s]'

    p = [list(set(CleanAndRemoveStopWords(re.sub(pattern, '', x)).split())) for x in JValues]
    JValuesRefined = []
    for x in p:
        JValuesRefined += x
    JValuesRefined = [x.replace('nbsp', '') for x in JValuesRefined]

    JValuesRefined = list(set(JValuesRefined))
    for i in JValuesRefined:
        if i in str(AValues).lower():
            ComplianceSet.add(i)
        else:
            NonComplianceSet.add(i)

    tempDict = {'TotalScore': 2}
    tempDict['ObtainedScore'] = np.minimum(2, (len(ComplianceSet) * 2) / (len(ComplianceSet) + len(NonComplianceSet)))
    tempDict['Detail'] = {'ComplianceSet': ComplianceSet, 'NonComplianceSet': NonComplianceSet}

    return tempDict


def getIndustryCompliance(JData, A_Data):
    Dict = {}
    if (JData == None):
        Dict['IndustryCompliance'] = 0
        Dict['IndustryComplianceSet'] = 'None'
        TempDict = {"Score": Dict['IndustryCompliance'], "Detail": Dict}

        return TempDict
    # get vector of the subindustry list

    Dict['IndustryGramSize'] = len(set(JData))

    AKeys = ['designition', 'skills', 'experience', 'jobExperience', 'university']
    if 'education' in A_Data.keys():
        AKeys.append('education')
        AKeys.append('certifications')
    if 'json_education' in A_Data.keys():
        AKeys.append('json_education')
        AKeys.append('json_certification')

    AValues = []
    for k in AKeys:
        try:
            AValues.append(A_Data[k])
        except:
            continue

    AValues = str(AValues)

    commonality = 0
    BiGramComplianceSet = []
    for i in JData:
        if len(i) > 0:
            if (i in AValues):
                BiGramComplianceSet.append(i)
                commonality += 1
    Dict['IndustryCompliance'] = len(set(BiGramComplianceSet))
    Dict['IndustryComplianceSet'] = set(BiGramComplianceSet)

    TempDict = {"Score": Dict['IndustryCompliance'], "Detail": Dict}
    return TempDict


############################### Gram base compliance###############
def GramCompliance(Aspect, JValues, AValues):
    UniDict = getUniGramCompliance(JValues, AValues)

    BiDict = getBiGramCompliance(JValues, AValues)

    return {**UniDict, **BiDict}


def getUniGramCompliance(JValues, AValues):
    UniDict = {}

    JUniGram = CleanAndRemoveStopWords(str(JValues)).split(' ')
    AUniGram = CleanAndRemoveStopWords(str(AValues)).split(' ')

    ComplianceSet = set(JUniGram).intersection(set(AUniGram))

    UniDict['UniGramSize'] = len(JUniGram)
    UniDict['UniGramScore'] = len(ComplianceSet)
    UniDict['UniGramComplianceSet'] = ComplianceSet
    return UniDict


def getBiGramCompliance(JValues, AValues):
    BiDict = {}
    JBiGrams = []

    for j in JValues:
        try:
            JBiGrams += stringToBiGrams(j)
        except:
            continue

    ABiGrams = []
    BiGrams = str(AValues).replace('  ', ' ')
    ABiGrams = stringToBiGrams(BiGrams)

    ComplianceSet = set(JBiGrams).intersection(set(ABiGrams))

    BiDict['BiGramSize'] = len(JBiGrams)
    BiDict['BiGramScore'] = len(ComplianceSet)
    BiDict['BiGramComplianceSet'] = ComplianceSet

    return BiDict


def stringToBiGrams(string):
    biGrams = []

    k = CleanAndRemoveStopWords(string).split(' ')
    for b in list(bigrams(k)):
        biGrams.append((b[0] + ' ' + b[1]))
    return biGrams


# %% Three forms from Job Data
def TransferIntoLiteral(JobData):
    J_LData = copy.copy(JobData)
    # clean = re.compile('<.*?>')
    # J_LData= re.sub(clean, '', J_LData)

    DontApplyOn = ['toolsHandlingExperience', 'subIndustry', 'location', 'city', 'degreeName', 'qualification',
                   'experience', 'city' 'nationalityPreference', 'educationWeightage', 'experienceWeightage',
                   'locationWeightage', 'skillsWeightage']
    for key, value in JobData.items():
        if key in DontApplyOn:
            continue
        if type(value) == list:
            valuelist = []
            for l in value:
                valuelist.append(clean(l))

            J_LData[key] = valuelist
        else:
            try:
                J_LData[key] = clean(value)
            except:
                J_LData[key] = value
    return J_LData


def TransferIntoBase(J_LData):
    J_BData = {}
    lemmatizer = WordNetLemmatizer()

    for key, value in J_LData.items():
        if len(str(value)) == 0:
            continue
        lemmatized_words = []
        if type(value) == list:
            valuelist = []
            for l in value:
                words = nltk.word_tokenize(l)

                lemma = []

                for word in words:
                    lemma.append(lemmatizer.lemmatize(word))
                valuelist.append(' '.join(lemma))

            # lemmatized_words.append(valuelist)
            J_BData[key] = valuelist


        else:
            try:
                words = nltk.word_tokenize(value)

                for word in words:
                    lemma = lemmatizer.lemmatize(word)
                    lemmatized_words.append(lemma)
            except:
                lemmatized_words = value
                J_BData[key] = value
                continue

            J_BData[key] = ' '.join(lemmatized_words)
    return J_BData


# %%  Clean Data and Remove stopwords
def getAndCleanJobData(JobUUID):
    JobData = requests.get(JOB_API + JobUUID, headers=API_HEADER).json()
    JobData = dict((k, JobData.get[k]) for k in JobDataRequiredKeys)

    for key, value in JobData.items():
        if isinstance(value, str):
            JobData[key] = value.lower()
        elif isinstance(value, list):
            JobData[key] = [x.lower() for x in value]

    if (JobData["subIndustry"] == None):
        return JobData, None
    query_body = {
        "query": {
            "match_all": {}
        }
    }

    JobVectors = ELASTIC_CLIENT.search(index="jobs", body=query_body)['hits']['hits']
    for i in JobVectors:
        if (i['_source']['category'] == JobData["subIndustry"]):
            break
    RelevantIndustryVector = i['_source']['Skills'] + i['_source']['tools'] + i['_source']['approaches']

    return JobData, RelevantIndustryVector


def CleanAndRemoveStopWords(string):
    cachedStopWords = ["including", "a", "about", "above", "after", "again", "against", "ain't", "all", "am", "an",
                       "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below",
                       "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
                       "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further",
                       "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
                       "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
                       "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
                       "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
                       "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
                       "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
                       "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
                       "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
                       "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
                       "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
                       "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
                       "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "also", "always",
                       "among", "another", "anybody", "anything", "anyway", "around", "away", "back", "believe", "call",
                       "can", "co", "com", "come", "done", "edu", "eg", "either", "else", "ever", "every", "everybody",
                       "get", "go", "going", "gone", "got", "hence", "hereby", "herein", "hereupon", "however", "ie",
                       "indeed", "last", "less", "let", "like", "may", "might", "mr", "mrs", "ms", "much", "must",
                       "namely", "neither", "never", "nevertheless", "next", "nobody", "none", "noone", "nothing",
                       "now", "nowhere", "often", "one", "onto", "per", "perhaps", "please", "put", "rather", "re",
                       "really", "said", "say", "see", "shall", "since", "somebody", "something", "sometimes", "still",
                       "therefore", "though", "thus", "together", "towards", "um", "unto", "upon", "us", "via", "well",
                       "whatever", "whence", "whenever", "whereby", "wherein", "whereupon", "wherever", "whether",
                       "whose", "will", "within", "without", "yet", "abst", "according", "ain", "albeit", "allow",
                       "allows", "allowed", "allow(s)", "already", "although", "amongst", "anyhow", "anyone", "anyways",
                       "anywhere", "apart", "appear", "appreciate", "appropriate", "a's", "aside", "ask", "asking",
                       "associated", "available", "awfully", "became", "become", "becomes", "becoming", "beforehand",
                       "behind", "beside", "besides", "best", "better", "beyond", "big", "brief", "c'mon", "c's",
                       "came", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "comes",
                       "concerning", "consequently", "consider", "considering", "contain", "containing", "contains",
                       "corresponding", "course", "currently", "definitely", "described", "despite", "different",
                       "downwards", "eight", "elsewhere", "enough", "entirely", "especially", "et", "etc", "even",
                       "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "far", "fifth",
                       "first", "five", "followed", "following", "follows", "former", "formerly", "forth", "four",
                       "furthermore", "gets", "getting", "given", "gives", "goes", "gotten", "greetings", "happens",
                       "hardly", "hello", "help", "hereafter", "hi", "hither", "hopefully", "howbeit", "ignored",
                       "immediate", "inasmuch", "inc", "indicate", "indicated", "indicates", "inner", "insofar",
                       "instead", "inward", "it'd", "it'll", "just", "keep", "keeps", "kept", "know", "known", "knows",
                       "lately", "later", "latter", "latterly", "least", "lest", "liked", "likely", "little", "look",
                       "looking", "looks", "ltd", "mainly", "many", "maybe", "mean", "meanwhile", "merely", "moreover",
                       "mostly", "name", "nd", "near", "nearly", "necessary", "need", "needs", "new", "nine", "non",
                       "normally", "novel", "obviously", "oh", "ok", "okay", "old", "ones", "others", "otherwise",
                       "outside", "overall", "particular", "particularly", "placed", "plus", "possible", "presumably",
                       "probably", "provides", "que", "quite", "qv", "rd", "reasonably", "regarding", "regardless",
                       "regards", "relatively", "respectively", "right", "saw", "saying", "says", "second", "secondly",
                       "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent",
                       "serious", "seriously", "seven", "several", "six", "somehow", "someone", "sometime", "somewhat",
                       "somewhere", "soon", "sorry", "specified", "specify", "specifying", "sub", "sup", "sure", "t's",
                       "take", "taken", "tell", "tends", "th", "thank", "thanks", "thanx", "thats", "thence",
                       "thereafter", "thereby", "therein", "theres", "thereupon", "think", "third", "thorough",
                       "thoroughly", "three", "throughout", "thru", "took", "toward", "tried", "tries", "truly", "try",
                       "trying", "twice", "two", "un", "unfortunately", "unless", "unlikely", "use", "used", "useful",
                       "uses", "using", "usually", "value", "various", "viz", "vs", "want", "wants", "way", "welcome",
                       "went", "whereafter", "whereas", "whither", "whoever", "whole", "willing", "wish", "wonder",
                       "yes", "zero", "obvsiously", "thither", "thx"]

    string = clean(string)
    string = ' '.join([word for word in string.split() if word not in cachedStopWords])
    return string


def clean(string):
    # remove special sybmols;
    # keep space and numbers
    # change case to lower
    # remove stop words
    # cleanString = " ".join(re.findall(r"[a-zA-Z0-9]+", string)).lower()

    clean = re.compile('<.*?>')
    cleanString = re.sub(clean, '', string)
    cleanString = cleanString.replace('\n', '')

    cleanString = cleanString.replace('\'s', 's').lower()
    cleanString = cleanString.replace('  ', ' ')
    cleanString = ' '.join([word for word in cleanString.split() if word not in cachedStopWords])
    return cleanString


# %% Collect Data
def getApplicantData(ApplicantsUUIDs):
    mydict = []
    for id in ApplicantsUUIDs:
        uniqueIdentifier = {"uniqueIdentifier.keyword": id}
        idstring = {'match': uniqueIdentifier}
        mydict.append(idstring)
    shouldDict = {'should': mydict}
    boolDict = {'bool': shouldDict}
    queryDict = {'query': boolDict}
    es = Elasticsearch(ELASTIC_LINK, basic_auth=("elastic", ELASTIC_PASS), verify_certs=False)

    result = es.search(index='search-resumes', body=queryDict)

    hits = result['hits']['hits']
    ApplicantsData = []
    foundIDs = []
    for ids in ApplicantsUUIDs:
        for hit in hits:
            if (ids == hit['_source']['uniqueIdentifier']):
                ApplicantsData.append(hit['_source'])
                foundIDs.append(ids)
                break
    notFoundIDs = set(ApplicantsUUIDs).difference(foundIDs)

    for ApplicantUUID in notFoundIDs:
        query_body = {"size": 1, "query": {"bool": {"must": {"match": {"uniqueIdentifier.keyword": ApplicantUUID}}}}}
        try:
            req = ELASTIC_CLIENT.search(index=Index, body=query_body)['hits']['hits'][0]['_source']
            ApplicantsData.append(req)
        except:
            continue

    return ApplicantsData
# Nova 5.0