import datetime
import zodiac


class Match:
    def __init__(self, user):  # enters as match.user
        self.bio = user.bio  # their biography
        self.name = user.name  # their name
        self.photos = user.photos  # a list of photo URLs
        # self.thumbnails = user.thumbnail  # a list of thumbnails of photo URLS
        self.age = user.age  # their age
        self.birth_date = user.birth_date  # their birth_date
        self.last_online = user.ping_time  # last online
        self.distance = user.distance_km  # distane from you
        self.common_friends = user.common_connections  # friends in common
        self.common_likes = user.common_interests  # likes in common - returns a list of {'name':NAME, 'id':ID}
        # user.get_photos(width=WIDTH)  # a list of photo URLS with either of these widths ["84","172","320","640"]
        # user.instagram_username  # instagram username
        # user.instagram_photos  # a list of instagram photos with these fields for each photo: 'image','link','thumbnail'
        self.schools = user.schools  # list of schools
        self.jobs = user.jobs  # list of jobs
        self.rank = 0.0

    def zodiac_sign(self):
        if (self.birth_date != None):
            bday = datetime.datetime.strptime("2013-1-25", '%Y-%m-%d').strftime('%m/%d/%y')
            sign = zodiac.getAstrologySign(zodiac.getMonth(bday), zodiac.getDay(bday))
            return sign

    def update_rank(self, amount):
        self.rank = self.rank + amount

    def closeness_to_distance_of_chosen_match(self, match_distance):
        if match_distance == self.distance:
            r = 1.0
        elif match_distance < self.distance:
            r = 1.0 - (float(self.distance - match_distance) / float(self.distance))
        else:
            r = 1.0 - (float(match_distance - self.distance) / float(match_distance))
        self.update_rank(r)

        # def get_introversion_level
