import pynder
import facebook
from Match import  Match
from Human import Human

# Unfortunately, we have to do this manually for now...
# 1. We find the auth_token by going to this address BUTTT:: https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token
# 2. BUTT... Before the url goes away really fast copy and paste the address bar after you hit enter.
#. 3. tHE auth token expires
auth_token = 'CAAGm0PX4ZCpsBAM2FAlAv7Okmw0fDtZATbNqfcePlxgmedFJh0omZCTJVGA7zWgEyX6idru1btNXW9WODEPvyIArPxIBYKVCHsMpNzKXjLhWyVY9bPsYSWS1ZCBoRvt8QR9rk7sfNRGF9C9WcdgZBi1FMlqurTKUT3KTVqw92Q5RAwOsiX23k9l9VRQoXfVz4YmMkQeLkPFZAg2hIlgkTw'
user = 'jackiehorowitz'


class Matchmaker:
    def __init__(self):
        # Get auth token here https://developers.facebook.com/tools/explorer/
        # facebook.get_app_access_token('1679708478963527', '38169c157e0b7f926e8ef5bddf88703b')
        self.session = pynder.Session(user, auth_token)
        self.matches = self.update_matches()
        self.current_user = Human(self.session.profile)

    # matches[2].get_photos()
       # print(matches[0].user.birth_date)
       # print(matchmaker.get_bios(matches, 30))

    def update_matches(self):
        matches = []
        for m in self.session.matches():
            if m !=None and m.user !=None:
                matches.append(Match(m.user))
        return matches

    def get_bios(self, matches, cnt):
        m = [n.user.bio for n in matches if
             n != None and n.user != None and n.user.bio != None and len(n.user.bio.split(' ')) > cnt]
        return m

