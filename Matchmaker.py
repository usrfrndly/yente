from Match import Match
from WatsonMagic import WatsonMagic
import numpy as np
import difflib
from operator import itemgetter


class Matchmaker:
    def __init__(self, api=None, matches=None, human=None):
        self.api = api
        self.matches = self.update_matches(matches)
        self.human = human
        self.human_preferences = {}
        self.watson = WatsonMagic()

        # print(self.current_user.bio)
        # self.human = self.set_human()
        # output2 = open('human_data.pkl', 'wb',  pickle.HIGHEST_PROTOCOL)
        # pickle.dump(self.human, output2)
        # output2.close()

    def update(self, apid):
        self.human_preferences = {}
        self.api = apid
        self.human = apid.profile()
        m = apid.matches()
        self.watson = WatsonMagic()
        self.matches = self.update_matches(self,m)

    def update_matches(self, mts):
        if mts is not None:
            matches = []
            for m in mts:
                if m is not None and m.user is not None:
                    matches.append(Match(m.user))
            return matches
        return None
            #
            # pkl_file = open('company_data.pkl', 'rb')
            # matches = pickle.load(pkl_file)
            #
            # pkl_file.close()
            # print(matches)
            # return matches

    def get_bios(self, matches, cnt):
        m = [n.bio.strip().rstrip('\n').replace('\n', '') for n in matches if
             n != None and n != None and n.bio != None and len(n.bio.split(' ')) > cnt]
        return m

    def calculate_social_rankings(self, social_prefs):
        self.human_preferences['social_prefs'] = social_prefs
        m_ranks = []
        for m in self.matches:
            m.clean_bio()
            if m is not None and m.bio is not None and len(m.bio.split(' ')) > 30:
                social_score = self.watson.get_tone_category_elements('social', m.bio)
                print(social_score)
                social_score_sorted = sorted(social_score,
                                             key=lambda x: x['score'])
                print("social_score_sorted" + str(social_score_sorted))
                m_ranks.append({m: social_score_sorted})
        human_social_prefs_named = [self.watson.SOCIAL_TONES[int(x) - 1] for x in social_prefs]
        m_ranks_named = {}
        for mr in m_ranks:
            for k, v in mr.items():
                tone_ranks = []
                for t in v:
                    tone_ranks.append(t['tone_name'])
                m_ranks_named[k] = tone_ranks

                #   m_ranks_named = [[m['tone_name'] for m in list(mr.values())] for mr in m_ranks]
        for m_named in m_ranks_named.keys():
            similarity = difflib.SequenceMatcher(None, tuple(human_social_prefs_named),
                                                 tuple(m_ranks_named[m_named])).ratio()
            m_named.update_rank(similarity, 'social_prefs')
            print(similarity)

    def calculate_distance_ranking(self, days_pref):
        self.human_preferences['days_per_week'] = days_pref
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
            base_match_value = np.percentile(a, int(percentile))  # return 50th percentile, e.g median.
            print(base_match_value)
            for m in self.matches:
                m.closeness_to_distance_of_chosen_match(base_match_value)

    def calculate_argument_ranking(self, argument_pref):
        argument_scores = []
        self.human_preferences['argument_pref'] = argument_pref

        for m in self.matches:
            m.clean_bio()
            if m is not None and m.bio is not None and len(m.bio.split(' ')) > 30:
                social_score_list = self.watson.get_tone_category_elements('social', m.bio)
                writing_score_list = self.watson.get_tone_category_elements('writing', m.bio)

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
                argument_score = (agreeable_score + analytic_score) / 2.0
                argument_scores.append({'match': m, 'score': argument_score})

        sorted_agreeable_scores = sorted(argument_scores, key=itemgetter('score'))

        print("sorted_agreeable_scores" + str(sorted_agreeable_scores))
        a = np.array([s['score'] for s in sorted_agreeable_scores])
        base_argument_value = np.percentile(a, 50)  # return 50th percentile, e.g median.
        print(base_argument_value)

        for agree_score in sorted_agreeable_scores:
            if argument_pref == 'Yes':
                agree_score['match'].update_rank(agree_score['score'], 'agreeable_score')
            elif argument_pref == 'No':
                agree_score['match'].update_rank(1.0 - agree_score['score'], 'agreeable_score')
            elif argument_pref == 'Maybe':
                agree_score['match'].closeness_to_argument_value_match(base_argument_value, agree_score['score'])

    def get_best_matches(self):
        best_matches = []
        for m in self.matches:
            best_matches.append((m, m.total_rank, m.ranked))
        best_matches = sorted(best_matches, key=lambda match: match[1], reverse=True)
        return best_matches

    # if __name__ == '__main__':
    # matchmaker = Matchmaker()
    # watson = WatsonMagic()
    # print(matchmaker.matches[2].photos)
    # print(matchmaker.matches[0].birth_date)
    # bios = matchmaker.get_bios(matchmaker.matches,10)
    # print("bios", bios)
    # c = ''.join(bios)
    # print("c " + c)
    # watson.extract_content_from_alchemy(c)
