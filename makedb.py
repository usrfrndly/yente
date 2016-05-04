import sqlite3 as lite
import sys
import Matchmaker
import pickle

if __name__ == '__main__':
    # auth_token = 'EAAGm0PX4ZCpsBACNZB4EZCiJNvZA6ZBiw9zZBF3jqZBDJ37rz6wZBOdTClZAIsVTOKEGnuVorXWdhfJyA1716JkMJ5SVJ7aHgz7qDlJgKO4M7Nbn28M4ZCQ0f8R00ZCDFDZAPXOmP8dHX4R6sIZAU21khK1aFQr0kIZAWhP9AHlUfSREk3nAZDZD'
    # user = 'jackiehorowitz'
    # s = pynder.Session(user, auth_token)
    # m = s.matches()
    # # matches = self.update_matches()
    # # #current_user = Human(self.session.profile)

    matm = Matchmaker.Matchmaker()
    output= open('company_data.pkl', 'wb')
    matches = matm.matches
    pickle.dump(matches, output, pickle.HIGHEST_PROTOCOL)
    output.close()

    input =  open('company_data.pkl', 'rb')
    matches = pickle.load(input)
    print(matches[0])  # -> banana
    print(matches[0].age)  # -> 40
    input.close()


