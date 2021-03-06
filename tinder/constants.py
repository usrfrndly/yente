REPORT_CAUSE_SPAM = 1
REPORT_CAUSE_INAPPROPRIATE = 2

GENDER_MALE = 0
GENDER_FEMALE = 1

GENDER_MAP = {'male': GENDER_MALE, 'female': GENDER_FEMALE}
GENDER_MAP_REVERSE = {GENDER_MALE: 'male', GENDER_FEMALE: 'female'}

PROFILE_FIELDS = [
    'gender', 'age_filter_min', 'age_filter_max', 'distance_filter',
    'bio', 'interested_in',
]

GLOBAL_HEADERS = {
    'app_version': '4',
    'platform': 'android',
    'user-agent': 'Tinder/4.0.9 (iPhone; iOS 8.1.1; Scale/2.00)',
}

DEFAULT_AUTH_FILE_PATH = '~/.pytinder.json'
