import json
from django.http import HttpResponse 
from pygrl.models import User


def users(request):
    user_lst = [u.to_dct() for u in User.objects.all()]
    return HttpResponse(json.dumps(user_lst))
