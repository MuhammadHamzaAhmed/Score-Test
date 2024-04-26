# from src.utils.config import CLAUDE_TOKEN
from anthropic import Anthropic


class Claude:

    def __init__(self, resume=""):
        self.anthropic = Anthropic(
            api_key="")
        self.prompt = (f"""I want you to parse my cv and give result in <p> tag your output should be"""
                       """<p>
               {
                   "name": "######",
                   "about_me": "ABOUT ME or OBJECTIVE or Profile or User description here",
                   "hobbies_interest": ["IF PRESENT", "IF PRESENT", "IF PRESENT"],
                   "contact_number": "######",
                   "email": "#####",
                   "skills": ["######", "######", "######"],
                   "other_skills" ["#######", "#######", "#######"],
                   "awards_honors" ["#######", "#######", "#######"],
                   "publications" ["#######", "#######", "#######"],
                   "languages": ["#####", "######", "######"],
                   "tools" : ["######", "######", "######"],
                   "json_certification": [
                     {
                        "name": "######",
                     },
                     {
                        "name": "######",
                     }
                   ],
                   "json_location": {
                     "city": "######",
                     "state": "#######(state or province)",
                     "country": "######"
                   },
                   "social_links": [
                     {
                        "platform": "######",
                        "url": "######"
                     },
                     {
                        "platform": "######",
                        "url": "######"
                     }
                   ],
                   "json_education": [
                      {
                         "school": "######",
                         "duration": "######",
                         "degree": "######"
                      },
                      {
                         "school": "######",
                         "duration": "######",
                         "degree": "######"
                      }
                   ],
                   "working_experience": [
                      {
                         "company": "######",
                         "duration": {
                            "years": "######",
                            "months": "######"
                         },
                         "position": "######",
                         "start_date": "######",
                         "end_date": "######",
                         "responsibilities": [
                            "######",
                            "######",
                            "######"
                         ]
                         
                      },
                      {
                         "company": "######",
                         "duration": {
                            "years": "######",
                            "months": "######"
                         },
                         "position": "######",
                         "start_date": "######",
                         "end_date": "######",
                         "responsibilities": [
                            "######",
                            "######",
                            "######"
                         ]
                         
                      }
                   ],
                   "json_projects": [
                    {
                        "name": "#######",
                        "description": [
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                        ],
                    },
                    {
                        "name": "#######",
                        "description": [
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                            "#######",
                        ],
                    },
                   ]
               }
               </p>
               make sure to enclosed every key and value in double quotes so that it is json.
               tools and skills are two different thing you must not add skills in tools and tools in skills even if user have added it.
               social links include linkedin, github, twitter, facebook, instagram, stackoverflow, medium, youtube.
               tools include programming languages, frameworks, libraries, databases, cloud services, operating systems,
                tools, methodologies, design patterns, etc.
               You need to fill ######. Here is my CV content\n
               ------ is optional if present then add it else discard that key.
               Your date format should be %b %Y. for month you will use
               Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec.
               for latest, ongoing or present job you should use present as end date
               """
                       f"""{resume}""")

    def predict_and_update(self):
        system = ("You will act as resume parser. Our client 3cix major focus on getting data related to working "
                  "experience. We will provide them with there desired output.")
        message = self.anthropic.messages.create(model="claude-3-haiku-20240307", max_tokens=4000, temperature=0,
                                                 system=system, messages=[
                {"role": "user", "content": [{"type": "text", "text": self.prompt}]}])
        return message.content[0].text

    def predict_text(self, text):
        system = "You will give score according to our requirement"
        message = self.anthropic.messages.create(model="claude-3-haiku-20240307", max_tokens=4000, temperature=0,
                                                 system=system, messages=[
                {"role": "user", "content": [{"type": "text", "text": text}]}])
        return message.content[0].text
