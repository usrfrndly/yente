import pynder
from Match import  Match
from Human import Human
import json
from watson_developer_cloud import ToneAnalyzerV3Beta

# Unfortunately, we have to do this manually for now...
# 1. We find the auth_token by going to this address BUTTT:: https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token
# 2. BUTT... Before the url goes away really fast copy and paste the address bar after you hit enter.
#. 3. tHE auth token expires

auth_token = 'EAAGm0PX4ZCpsBAG7KQAZCyOLTunlxvW3ps09zhPW3gqJnAFXJThMYvszzUm4vtZA4pVXUdMJZAZCV6u1XSUSXWeyVpqIiRwMSXOtfA0SVY1bltXOEzRW9M4ZALQU3GMBkbhWFkq7PG8ZBZANs0qWdGE3SbnDhnDVyKuUyZAge4INYSgZDZD'
user = 'jackiehorowitz'


class Matchmaker:
    def __init__(self):
        # Get auth token here https://developers.facebook.com/tools/explorer/
        # facebook.get_app_access_token('1679708478963527', '38169c157e0b7f926e8ef5bddf88703b')
        self.session = pynder.Session(user, auth_token)
        self.matches = self.update_matches()
        self.current_user = Human(self.session.profile)



    def update_matches(self):
        matches = []
        for m in self.session.matches():
            if m !=None and m.user !=None:
                matches.append(Match(m.user))
        return matches

    def get_bios(self, matches, cnt):
        m = [n.bio.strip().rstrip('\n').replace('\n','') for n in matches if
             n != None and n != None and n.bio != None and len(n.bio.split(' ')) > cnt]
        return m

if __name__ == '__main__':
    matchmaker = Matchmaker()
    print(matchmaker.matches[2].photos)
    print(matchmaker.matches[0].birth_date)
    print(matchmaker.get_bios(matchmaker.matches, 30))
    tone_analyzer = ToneAnalyzerV3Beta(
        username='1a60da93-fd3f-4757-822d-a71fa8c126ca',
        password='ijUcTtmJPra7',
        version='2016-02-11')

    print(json.dumps(tone_analyzer.tone(text='I am very happy'), indent=2))
    print(tone_analyzer.tone(text='I am very happy')['document_tone']['tone_categories'][2]['tones'].values())
