from watson_developer_cloud import ToneAnalyzerV3Beta
import json
from collections import Counter
import time
from alchemyapi import AlchemyAPI
class WatsonMagic:
    SOCIAL_TONES = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Emotional Range']
    ENTITY_MAPPING = {'City':'cities', 'Person':'people', 'JobTitle':'jobs', 'Organization':'organizations', 'Company':'companies', 'Sport':'sports', 'PrintMedia':'media', 'Country':'countries', 'FieldTerminology':'terms', 'StateOrCounty':'places', 'Holiday':'holidays'}

    def __init__(self):
        self.tone_analyzer = ToneAnalyzerV3Beta(
            username='1a60da93-fd3f-4757-822d-a71fa8c126ca',
            password='ijUcTtmJPra7',
            version='2016-02-11')
        self.alchemyapi = AlchemyAPI()
        self.entities = {}


    def extract_type_entities_from_alchemy(self, text):
        types = {}
        response = self.alchemyapi.entities('text', text, {'sentiment': 0})

        if response['status'] == 'OK':
            for entity in response['entities']:
                if entity['type'] in types:
                    types[entity['type']].append((entity['text'],entity))
                else:
                    types[entity['type']] = [(entity['text'],entity)]
            print("[*] Retrieved {} entities from {}".format(len(self.entities), text))
        else:
            print("[!] Error receiving Alchemy response: %s" % response['statusInfo'])
        time.sleep(1)
        # now accumulate our most common terms and print them out
        sorted_type_keys = sorted(types, key=lambda x: len(types[x]),reverse=True)
        print(sorted_type_keys)
        sorted_types = []
        for k in sorted_type_keys:
            sorted_types.append(types[k])
        return sorted_types


        #   types_counter = Counter(types)
      #  top_types = types_counter.most_common()
       # print(top_types)
        #return top_types[0:5]

    def extract_most_popular_entitiesfrom_alchemy(self, text):
        response = self.alchemyapi.entities('text', text, {'sentiment': 0})

        if response['status'] == 'OK':

            # loop through the list of entities
            for entity in response['entities']:

                # add each entity to our master list
                if entity['text'] in self.entities:
                    self.entities[entity['text']] += int(entity['count'])
                else:
                    self.entities[entity['text']] = int(entity['count'])
            print("[*] Retrieved {} entities from {}".format(len(self.entities), text))
        else:
            print("[!] Error receiving Alchemy response: %s" % response['statusInfo'])

        time.sleep(1)
        # now accumulate our most common terms and print them out
        entity_counter = Counter(self.entities)

        top_entities = entity_counter.most_common()

        # let's take the top 10 entities UBL mentions
        for top_entity in top_entities[0:10]:
            # most_common returns a tuple (entity,count)
            print("%s => %d" % (top_entity[0], top_entity[1]))

    def get_tone_category_elements(self,category,text):
        t = self.tone_analyzer.tone(text=text, tones=category)['document_tone']['tone_categories'][0]['tones']

        return t
