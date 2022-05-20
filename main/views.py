import datetime

import requests

from django.shortcuts import render, redirect

from control.settings import env

from . import auth
from .const import AUTH_ABS_URL


@auth.is_authenticated
def home(request):
    print(request.COOKIES.get('user_id'))
    return render(request, 'home.html', {'location_list': [1]})


def welcome(request):
    context = {
        'api_id': env('VK_API_ID'),
        'auth_uri': AUTH_ABS_URL
    }
    return render(request, 'welcome.html', context)


def auth_confirm(request):
    code = request.GET['code']
    aid = env('VK_API_ID')
    secret = env('VK_API_SECRET')
    redirect_uri = 'http://127.0.0.1:8000/auth'

    vk_response = requests.get('https://oauth.vk.com/access_token', params={
        'client_id': aid,
        'client_secret': secret,
        'redirect_uri': redirect_uri,
        'code': code,
    })
    vk_content = vk_response.json()

    resp = redirect('/')
    resp.set_cookie('user_id', vk_content['user_id'])
    resp.set_cookie('access_token', vk_content['access_token'])
    resp.set_cookie('created_at', datetime.datetime.utcnow().timestamp())
    resp.set_cookie('expires_in', vk_content['expires_in'])
    return resp


@auth.is_authenticated
def logout(request):
    resp = redirect('/welcome')
    resp.delete_cookie('user_id')
    resp.delete_cookie('access_token')
    resp.delete_cookie('created_at')
    resp.delete_cookie('expires_in')
    return resp
