import datetime

import requests

from django.shortcuts import redirect

from control.settings import env
from .models import User


def is_authenticated(view):
    def wrapper(request):
        uid = request.COOKIES.get('user_id')
        access_token = request.COOKIES.get('access_token')
        created_at = request.COOKIES.get('created_at')
        expires_in = request.COOKIES.get('expires_in')

        # Check if the user was authenticated earlier
        if not (uid and access_token and created_at and expires_in):
            return redirect('/welcome')

        # Token expired validation
        created_at = datetime.datetime.fromtimestamp(float(created_at))
        expires_in = datetime.timedelta(seconds=int(expires_in))

        if created_at + expires_in < datetime.datetime.utcnow():
            return redirect('/welcome')

        return view(request)
    return wrapper
