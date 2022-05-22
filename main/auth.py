import datetime

from django.shortcuts import redirect

from control.settings import TESTING


def is_authenticated(view):
    def wrapper(request):
        if TESTING:
            return view(request)
        uid = request.COOKIES.get('uid')
        access_token = request.COOKIES.get('access_token')
        created_at = request.COOKIES.get('created_at')
        expires_in = request.COOKIES.get('expires_in')

        # Check if the user was authenticated earlier
        if not all((uid, access_token, created_at, expires_in)):
            return redirect('/welcome')

        # Token expired validation
        created_at = datetime.datetime.fromtimestamp(float(created_at))
        expires_in = datetime.timedelta(seconds=int(expires_in))

        if created_at + expires_in < datetime.datetime.utcnow():
            return redirect('/welcome')

        return view(request)
    return wrapper


def is_not_authenticated(view):
    def wrapper(request):
        if TESTING:
            return view(request)

        uid = request.COOKIES.get('uid')
        access_token = request.COOKIES.get('access_token')
        created_at = request.COOKIES.get('created_at')
        expires_in = request.COOKIES.get('expires_in')

        # Token expired validation
        if created_at and expires_in:
            created_at = datetime.datetime.fromtimestamp(float(created_at))
            expires_in = datetime.timedelta(seconds=int(expires_in))

        # Check if the user is authenticated
        if all((uid, access_token, created_at, expires_in)) and created_at + expires_in >= datetime.datetime.utcnow():
            return redirect('/')

        return view(request)
    return wrapper
