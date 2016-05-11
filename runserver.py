import os
from flask import Flask, request, render_template, url_for, redirect, flash, make_response
from Matchmaker import Matchmaker as m
import WatsonMagic
from tinder import utils, api

app = Flask(__name__)
app.secret_key = 'secretKey'
app.m = m
@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method=='POST':
        apid = api.API(debug=True)
        try:
            toke = utils.get_tinder_access_token(request.form['username'], request.form['password'])
            apid.set_auth(request.form['username'], toke)
            print(apid.authorize())
            m.update(m,apid=apid)
            return redirect('/questions')
        except Exception as e:
            return render_template('login.html', error=e)




@app.route('/questions')
def questions():
    return render_template('questions.html', social_tones=WatsonMagic.WatsonMagic.SOCIAL_TONES)


@app.route('/results', methods=['GET', 'POST'])
def get_results():
    if request.method == 'GET':
        return render_template('results.html')
    if request.method == 'POST':
        print("distance pref: " + request.form['form-days-per-week'])
        social_prefs = request.form["social-rankings"].replace('ranking[]=', '').split('&')
       # print("social ranks pref: " + str(social_prefs))
        m.calculate_social_rankings(m,social_prefs)
        m.calculate_distance_ranking(m,request.form['form-days-per-week'])
        print("argument pref: " + request.form['argumentsRadio'])
        m.calculate_argument_ranking(m,request.form['argumentsRadio'])

        best_matches = m.get_best_matches(m)
        return render_template('results.html', bestmatches=best_matches)


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    app.run( debug=True)
