# from src.utils.config import CLAUDE_TOKEN
from anthropic import Anthropic


class Claude:

    def __init__(self, ):
        self.anthropic = Anthropic(api_key="")

    def predict_and_update(self):
        system = ("You will act as resume parser. Our client 3cix major focus on getting data related to working "
                  "experience. We will provide them with there desired output.")
        message = self.anthropic.messages.create(model="claude-3-haiku-20240307", max_tokens=4000, temperature=0,
                                                 system=system, messages=[
                {"role": "user", "content": [{"type": "text", "text": self.prompt}]}])
        return message.content[0].text

    def predict_score(self, text):
        system = "You will give score according to our requirement"
        message = self.anthropic.messages.create(model="claude-3-sonnet-20240229", max_tokens=4000, temperature=0,
                                                 system=system, messages=[
                {"role": "user", "content": [{"type": "text", "text": text}]}])
        return message.content[0].text

    def predict_summary(self, text):
        system = "You will generate summary according to our requirement"
        message = self.anthropic.messages.create(model="claude-3-haiku-20240307", max_tokens=4000, temperature=0,
                                                 system=system, messages=[
                {"role": "user", "content": [{"type": "text", "text": text}]}])
        return message.content[0].text
