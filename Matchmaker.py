import pynder
from Match import Match
from WatsonMagic import WatsonMagic
from watson_developer_cloud import ToneAnalyzerV3Beta
import numpy as np
import pickle
import difflib
from operator import itemgetter

# Unfortunately, we have to do this manually for now...
# 1. We find the auth_token by going to this address BUTTT:: https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token
# 2. BUTT... Before the url goes away really fast copy and paste the address bar after you hit enter.
# . 3. tHE auth token expires
auth_token = 'EAAGm0PX4ZCpsBAFs8tBRJZBdIGOE1QlwVCm79i4LqybSHbxq9hK7Gn3D91MenRvSfmQf6rMBQzOHj7jVqauV7EZCWyflIBXl8ez6YyLkPvfF0QIGtriBH12UkTPZCTqlr04atMPTlQk4TsBvhBzeIus5XiXDmO65OecOf8fyugZDZD'
user = 'jackiehorowitz'

class Matchmaker:
    def __init__(self):
        # Get auth token here https://developers.facebook.com/tools/explorer/
        # facebook.get_app_access_token('1679708478963527', '38169c157e0b7f926e8ef5bddf88703b')
      #  self.session = pynder.Session(user, auth_token)
        self.matches = self.update_matches()
        #self.profile = self.session.profile
        self.watson =  WatsonMagic()

        self.human = self.set_human()
        #       self.current_user = Human(self.session.profile))

        # print(self.current_user.bio)
        # self.human = self.set_human()
        # output2 = open('human_data.pkl', 'wb',  pickle.HIGHEST_PROTOCOL)
        # pickle.dump(self.human, output2)
        # output2.close()

    def set_human(self):
        pkl_file = open('human_data.pkl', 'rb')
        human = pickle.load(pkl_file)
        pkl_file.close()
        print(human)
        return human

       #  h={}
       #  h['bio']=self.profile.bio
       #  h['age_max']= self.profile.age_filter_max
       #  h['age_min']=self.profile.age_filter_min
       #  h['create_date'] =self.profile.create_date
       #  h['distance_filter'] = self.profile.distance_filter
       #      # 'gender': self.profile.gender,
       #      # 'interested_in': self.profile.interested_in
       # # h['name']= self.profile.name
       #      # 'last_active': self.profile.ping_time,
       #  h['preferences'] = {}
       #
       #  return h

    def update_matches(self):
        #matches = []
        # for m in self.session.matches():
        #     if m != None and m.user != None:
        #         matches.append(Match(m.user))
        # return matches

        pkl_file = open('company_data.pkl', 'rb')
        matches = pickle.load(pkl_file)

        pkl_file.close()
        print(matches)
        return matches

    def get_bios(self, matches, cnt):
        m = [n.bio.strip().rstrip('\n').replace('\n', '') for n in matches if
             n != None and n != None and n.bio != None and len(n.bio.split(' ')) > cnt]
        return m


    def calculate_social_rankings(self, social_prefs):
        self.human['preferences']['social_prefs'] = social_prefs
        m_ranks = []
        for m in self.matches: 
            m.clean_bio()
            if m != None  and m.bio != None and len(m.bio.split(' ')) > 30:
                social_score = self.watson.get_tone_category_elements('social',m.bio)
                print(social_score)
                social_score_sorted = sorted(social_score,
                                             key=lambda x: x['score'])
                print("social_score_sorted" + str(social_score_sorted))
                m_ranks.append({m:social_score_sorted})
        #see which matches have the most similar lists
        human_social_prefs_named = [self.watson.SOCIAL_TONES[int(x)-1] for x in social_prefs]
        m_ranks_named={}
        for mr in m_ranks:
            for k, v in mr.items():
                tone_ranks = []
                for t in v:
                    tone_ranks.append(t['tone_name'])
                m_ranks_named[k] = tone_ranks

     #   m_ranks_named = [[m['tone_name'] for m in list(mr.values())] for mr in m_ranks]
        for m_named in m_ranks_named.keys():
            similarity = difflib.SequenceMatcher(None, tuple(human_social_prefs_named), tuple(m_ranks_named[m_named])).ratio()
            m_named.update_rank(similarity,'social_prefs')
            print(similarity)


    def calculate_distance_ranking(self, days_pref):
        self.human['preferences']['days_per_week'] = days_pref
        matches_by_distance = sorted(self.matches,
                                     key=lambda x: x.distance)
        percentile = (float(days_pref) / 7.0) * 100.0
        if percentile == 100.0:
            base_match_value = matches_by_distance[len(matches_by_distance) - 1]
        elif percentile == 0.0:
            base_match_value = matches_by_distance[0]
        else:
            print([m.distance for m in matches_by_distance])
            a = np.array([m.distance for m in matches_by_distance])
            base_match_value = np.percentile(a, percentile)  # return 50th percentile, e.g median.
            print(base_match_value)
            for m in self.matches:
                m.closeness_to_distance_of_chosen_match(base_match_value)

    def calculate_argument_ranking(self, argument_pref):
        argument_scores = []
        for m in self.matches:
            m.clean_bio()
            if m != None  and m.bio != None and len(m.bio.split(' ')) > 30:
                social_score_list = self.watson.get_tone_category_elements('social',m.bio)
                writing_score_list = self.watson.get_tone_category_elements('writing',m.bio)

                print(social_score_list)
                print(writing_score_list)
                agreeable_score = 0.0
                analytic_score = 0.0
                for social_dct in social_score_list:
                    if social_dct['tone_name'] == 'Agreeableness':
                        agreeable_score += social_dct['score']
                for writing_dct in writing_score_list:
                    if writing_dct['tone_name'] == 'Analytical':
                        analytic_score += writing_dct['score']
                argument_score = (agreeable_score + analytic_score)/2.0
                argument_scores.append({'match':m,'score':argument_score})

        sorted_agreeable_scores = sorted(argument_scores, key=itemgetter('score'))

        print("sorted_agreeable_scores" + str(sorted_agreeable_scores))
        a = np.array([s['score'] for s in sorted_agreeable_scores])
        base_argument_value = np.percentile(a, 50)  # return 50th percentile, e.g median.
        print(base_argument_value)

        for agree_score in sorted_agreeable_scores:
            if argument_pref == 'Yes':
                agree_score['match'].update_rank('agreeable_score',agree_score['score'])
            elif argument_pref == 'No':
                agree_score['match'].update_rank('agreeable_score',1.0-agree_score['score'])
            elif argument_pref == 'Maybe':
                agree_score['match'].closeness_to_argument_value_match(base_argument_value,agree_score['score'])



if __name__ == '__main__':
    matchmaker = Matchmaker()
    print(matchmaker.matches[2].photos)
    print(matchmaker.matches[0].birth_date)
    bios = matchmaker.get_bios(matchmaker.matches,10)
    print(bios)
    #watson.get_tone_category_elements(text=bios[0],category='social')



