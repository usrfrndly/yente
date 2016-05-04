import os
from flask import Flask, request, render_template, url_for, redirect,session,flash, make_response
from Matchmaker import Matchmaker
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

# import config
app = Flask(__name__)
# authomatic = Authomatic(config.CONFIG, 'gdfsgdsfgdsf', report_errors=False)

global matchmaker
matchmaker = Matchmaker()
@app.route('/')
def index():
	return render_template("questions.html")
	#return redirect('https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token')

# @app.route('/login/<provider_name>/', methods=['GET', 'POST'])
# def login(provider_name):
#     response = make_response()
#     result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
#     if result:
#         if result.error:
#             return 'Something went wrong: {0}'.format(result.error.message)
#         if result.user:
#             result.user.update()
#         return render_template('login.html', result=result)
#     return response

@app.route('/pynderbot', methods=['POST'])
def pynderbot():
	global userId, accessToken
	userId = request.form['userId']
	accessToken = request.form['accessToken']
	
	print(userId)
	print(accessToken)

	return render_template("../../../../../Google Drive/Python Apps/LoveBot/templates/pynderbot.html")


@app.route('/like')
def like():
	print(userId)
	print(accessToken)
	# session = pynder.Session(str(userId), str(accessToken))
	# users = session.nearby_users()
	# liked = []
	# for user in users[:5]:
	# 	user.like()
	# 	liked.append(user.name)
    #
	# return render_template("like.html", liked=liked)

if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    app.run(port=8080, debug=True)