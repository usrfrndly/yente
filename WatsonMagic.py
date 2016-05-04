from watson_developer_cloud import ToneAnalyzerV3Beta
import json
class WatsonMagic:
    SOCIAL_TONES = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Emotional Range']

    def __init__(self):
        self.tone_analyzer = ToneAnalyzerV3Beta(
            username='1a60da93-fd3f-4757-822d-a71fa8c126ca',
            password='ijUcTtmJPra7',
            version='2016-02-11')


    def get_tone_category_elements(self,category,text):
        t = self.tone_analyzer.tone(text=text, tones=category)['document_tone']['tone_categories'][0]['tones']
        return t
