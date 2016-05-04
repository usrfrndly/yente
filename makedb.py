import sqlite3 as lite
import sys
import Matchmaker
import pickle

matm = Matchmaker.Matchmaker()
output = open('company_data.pkl', 'wb')
matches = matm.matches
pickle.dump(matches, output, pickle.HIGHEST_PROTOCOL)
output.close()
#
# input =  open('company_data.pkl', 'rb')
# matches = pickle.load(input)
# print(matches[0])  # -> banana
# print(matches[0].age)  # -> 40
# input.close()
