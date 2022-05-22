import datetime
import json

import requests
import folium

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


from control.settings import env

from . import auth
from .models import User, Memory
from .const import AUTH_ABS_URL
from .forms import AddMemoryForm


def get_user_info(uid: int) -> dict:
    db_info = User.objects.get(uid=uid)
    full_name = f'{db_info.first_name} {db_info.last_name}'
    return {
        'name': full_name,
        'avatar': db_info.avatar,
    }


def create_map(uid: int) -> folium.Map:
    m = folium.Map(location=[63.391522, 96.328125], zoom_start=2)

    for marker in Memory.objects.filter(user=uid):
        folium.Marker(
            [marker.latitude, marker.longitude],
            popup=marker.place,
            draggable=None,
            icon=folium.Icon(icon='heart', color='red', icon_color='white'),
        ).add_to(m)

    m.add_child(folium.LatLngPopup())
    m.add_child(folium.ClickForMarker())
    return m


@auth.is_authenticated
def home(request):
    uid = request.COOKIES.get('user_id')

    user_info = get_user_info(uid)

    memories = Memory.objects.filter(user=uid)
    indexes = list(range(1, len(memories) + 1))

    context = {
        'name': user_info['name'],
        'avatar': user_info['avatar'],
        'location_list': list(zip(indexes, memories)),
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


@csrf_exempt
@auth.is_authenticated
def handle_map(request):
    uid = request.COOKIES.get('user_id')

    if request.method == 'POST':
        resp_content = json.loads(request.body)
        Memory.objects.create(
            user=uid,
            latitude=resp_content['latitude'],
            longitude=resp_content['longitude'],
            place=resp_content['place'],
            description=resp_content['description'],
        )

    user_info = get_user_info(uid)
    add_form = AddMemoryForm()
    m = create_map(uid)
    context = {
        'name': user_info['name'],
        'avatar': user_info['avatar'],
        'map': m._repr_html_(),
        'add_form': add_form,
    }
    return render(request, 'map.html', context)
