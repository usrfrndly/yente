from watson_developer_cloud import ToneAnalyzerV3Beta
import json
SOCIAL_TONES = ['Openness','Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
class WatsonMagic:
    def __init__(self):
        self.tone_analyzer = ToneAnalyzerV3Beta(
            username='1a60da93-fd3f-4757-822d-a71fa8c126ca',
            password='ijUcTtmJPra7',
            version='2016-02-11')


    def get_tone_category_elements(self,category,text):
        print(json.dumps(self.tone_analyzer.tone(text=text, tones=category), indent=2))
