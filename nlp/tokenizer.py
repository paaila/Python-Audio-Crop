import re


# This converts the encoded text to an internal unicode object, where
# all characters are properly recognized as an entity:
class SentenceTokenizer:

    def __init__(self, seperators=["।", "?", "\n"]):
        self.seperators = seperators
        self.regex = re.compile('[' + ''.join(seperators) + ']')
        pass

    def __iter__(self):
        return self

    def tokenize(self, text: str):
        text=text.replace('\n', ' ')
        return [x.strip() for x in self.regex.split(text)]


nepali_tokenizer = SentenceTokenizer()
