import datetime
from typing import Union

from django.shortcuts import redirect, reverse

from control.settings import TESTING


def get_uid(request) -> Union[int, None]:
    """Handles user id from cookie"""
    uid = request.COOKIES.get("uid")

    if uid is None:
        return None

    if isinstance(uid, str) and not uid.isdigit():
        return None

    return int(uid)


def is_authenticated(view):
    def wrapper(request):
        uid = get_uid(request)
        if TESTING:
            return view(request, uid)
        access_token = request.COOKIES.get("access_token")
        created_at = request.COOKIES.get("created_at")
        expires_in = request.COOKIES.get("expires_in")

        # Check if the user was authenticated earlier
        if not all((uid, access_token, created_at, expires_in)):
            return redirect(reverse("welcome"))

        # Token expired validation
        created_at = datetime.datetime.fromtimestamp(float(created_at))
        expires_in = datetime.timedelta(seconds=int(expires_in))

        if created_at + expires_in < datetime.datetime.utcnow():
            return redirect(reverse("welcome"))

        return view(request, uid)

    return wrapper


def is_not_authenticated(view):
    def wrapper(request):
        if TESTING:
            return view(request)

        uid = get_uid(request)
        access_token = request.COOKIES.get("access_token")
        created_at = request.COOKIES.get("created_at")
        expires_in = request.COOKIES.get("expires_in")

        # Token expired validation
        if created_at and expires_in:
            created_at = datetime.datetime.fromtimestamp(float(created_at))
            expires_in = datetime.timedelta(seconds=int(expires_in))

        # Check if the user is authenticated
        if (
            all((uid, access_token, created_at, expires_in))
            and created_at + expires_in >= datetime.datetime.utcnow()
        ):
            return redirect("/")

        return view(request)

    return wrapper
