import datetime

import requests
import folium

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from control.settings import env

from . import auth
from .models import User
from .const import AUTH_ABS_URL


def create_map() -> folium.Map:
    m = folium.Map(location=[63.391522, 96.328125], zoom_start=2)
    m.add_child(folium.LatLngPopup())
    return m


@auth.is_authenticated
def home(request):
    uid = request.COOKIES.get('user_id')
    user_info = User.objects.get(uid=uid)
    full_name = f'{user_info.first_name} {user_info.last_name}'

    map_widget = folium.Map()
    # map_widget = map_widget._repr_html_()

    context = {
        'name': full_name,
        'avatar': user_info.avatar,
        'map': map_widget,
        'location_list': [1],
    }
    return render(request, 'home.html', context)


@auth.is_not_authenticated
def welcome(request):
    context = {
        'api_id': env('VK_API_ID'),
        'auth_uri': AUTH_ABS_URL,
        'page': 'page',
    }
    return render(request, 'welcome.html', context)


def auth_confirm(request):
    code = request.GET['code']
    aid = env('VK_API_ID')
    secret = env('VK_API_SECRET')
    redirect_uri = AUTH_ABS_URL

    vk_response = requests.get('https://oauth.vk.com/access_token', params={
        'client_id': aid,
        'client_secret': secret,
        'redirect_uri': redirect_uri,
        'code': code,
    })
    vk_access_content = vk_response.json()

    if not User.objects.filter(uid=vk_access_content['user_id']).exists():
        user_content = requests.get('https://api.vk.com/method/users.get?user_id=210700286&v=5.131', params={
            'access_token': env('VK_SECURE_ACCESS_TOKEN'),
            'user_ids': vk_access_content.get('user_id'),
            'fields': ['photo_100'],
            'v': 5.131,
            'lang': 0,
        }).json()['response'][0]

        User.objects.create(uid=user_content['id'],
                            first_name=user_content['first_name'],
                            last_name=user_content['last_name'],
                            avatar=user_content['photo_100'],
                            )

    resp = redirect('/')
    resp.set_cookie('user_id', vk_access_content['user_id'])
    resp.set_cookie('access_token', vk_access_content['access_token'])
    resp.set_cookie('created_at', datetime.datetime.utcnow().timestamp())
    resp.set_cookie('expires_in', vk_access_content['expires_in'])
    return resp


@auth.is_authenticated
def logout(request):
    resp = redirect('/welcome')
    resp.delete_cookie('user_id')
    resp.delete_cookie('access_token')
    resp.delete_cookie('created_at')
    resp.delete_cookie('expires_in')
    return resp


@xframe_options_exempt
@auth.is_authenticated
def handle_map(request):
    uid = request.COOKIES.get('user_id')
    # Получаю координаты меток

    m = create_map()
    return HttpResponse(m._repr_html_())
