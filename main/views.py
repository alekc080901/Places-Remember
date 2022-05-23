import datetime
import json
import math
from typing import Union

import folium
import requests
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from control.settings import env

from . import auth
from .const import AUTH_ABS_URL, DEFAULT_LOCATION, DEFAULT_START_ZOOM
from .custom_folium import EditedClickForMarker, EditedLatLngPopup
from .forms import AddMemoryForm
from .models import Memory, User, Token


def scale_to_zoom(uid: int, scale: str) -> Union[int, None]:
    """Transforms scale of the map to folium zoom number"""
    if (
        not isinstance(scale, str)
        and not isinstance(scale, int)
        and not isinstance(scale, float)
    ):
        return None
    if isinstance(scale, str) and scale.lower() == "default":
        memories = Memory.objects.filter(user=uid)
        if memories.count() == 0:
            return DEFAULT_START_ZOOM
        else:
            return memories[memories.count() - 1].zoom

    return int(math.log2(int(scale))) + 1


def get_user_info(uid: int) -> dict:
    """Return full name and avatar of user by id"""
    db_info = get_object_or_404(User, uid=uid)
    full_name = f"{db_info.first_name} {db_info.last_name}"
    return {
        "name": full_name,
        "avatar": db_info.avatar,
    }


def create_map(uid: int) -> folium.Map:
    """Creates user map that reflects the user markers and last location on the map"""
    markers = []
    zoom = DEFAULT_START_ZOOM
    location = DEFAULT_LOCATION
    for marker in Memory.objects.filter(user=uid):
        location = (marker.latitude, marker.longitude)
        zoom = marker.zoom

        markers.append(
            folium.Marker(
                location,
                popup=marker.place,
                draggable=None,
                icon=folium.Icon(icon="heart", color="red", icon_color="white"),
            )
        )

    m = folium.Map(location=location, zoom_start=zoom)
    [marker.add_to(m) for marker in markers]

    m.add_child(EditedLatLngPopup())
    m.add_child(EditedClickForMarker())
    return m


@auth.is_authenticated
def home(request, uid):
    if uid is None:
        return redirect(reverse("welcome"))

    if request.method == "DELETE":
        request_json = json.loads(request.body)

        if "id" not in request_json:
            return HttpResponse(status=400)

        try:
            loc_id = int(request_json["id"])
            deleted_memory = Memory.objects.get(id=loc_id)
            deleted_memory.delete()
        except (ValueError, IndexError):
            return HttpResponse(status=400)

        return JsonResponse(
            {
                "id": loc_id,
            }
        )

    user_info = get_user_info(uid)

    memories = Memory.objects.filter(user=uid)
    indexes = list(range(1, len(memories) + 1))

    context = {
        "name": user_info["name"],
        "avatar": user_info["avatar"],
        "location_list": list(zip(indexes, memories)),
        "location_object": [model_to_dict(x) for x in memories]
    }

    return render(request, "home.html", context)


@auth.is_not_authenticated
def welcome(request):
    context = {
        "api_id": env("VK_API_ID"),
        "auth_uri": AUTH_ABS_URL,
        "page": "page",
    }
    return render(request, "welcome.html", context)


def auth_confirm(request):
    code = request.GET["code"]
    aid = env("VK_API_ID")
    secret = env("VK_API_SECRET")
    redirect_uri = AUTH_ABS_URL

    vk_response = requests.get(
        "https://oauth.vk.com/access_token",
        params={
            "client_id": aid,
            "client_secret": secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    vk_access_content = vk_response.json()

    if vk_access_content.get('error', None) is not None:
        return HttpResponse(status=400)

    uid = vk_access_content.get("user_id")
    access_token = vk_access_content.get("access_token")

    Token.objects.update_or_create(uid=uid, defaults={'access_token': access_token})

    if not User.objects.filter(uid=uid).exists():
        user_content = requests.get(
            "https://api.vk.com/method/users.get?",
            params={
                "access_token": env("VK_SECURE_ACCESS_TOKEN"),
                "uids": uid,
                "fields": ["photo_100"],
                "v": 5.131,
                "lang": 0,
            },
        ).json()["response"][0]

        User.objects.create(
            uid=user_content["id"],
            first_name=user_content["first_name"],
            last_name=user_content["last_name"],
            avatar=user_content["photo_100"],
        )

    resp = redirect(reverse("home"))
    resp.set_cookie("uid", vk_access_content["user_id"])
    resp.set_cookie("access_token", access_token)
    resp.set_cookie("created_at", datetime.datetime.utcnow().timestamp())
    resp.set_cookie("expires_in", vk_access_content["expires_in"])
    return resp


@auth.is_authenticated
def logout(request, uid):
    Token.objects.filter(uid=uid).delete()

    resp = redirect(reverse("welcome"))
    resp.delete_cookie("uid")
    resp.delete_cookie("access_token")
    resp.delete_cookie("created_at")
    resp.delete_cookie("expires_in")
    return resp


@csrf_exempt
@auth.is_authenticated
def map_handle(request, uid):
    if request.method == "POST":
        resp_content = json.loads(request.body)

        fields = ("latitude", "longitude", "scale", "place", "description")
        if any(field not in resp_content for field in fields):
            return HttpResponse(status=400)

        try:
            new_memory = Memory.objects.create(
                user=uid,
                latitude=resp_content["latitude"],
                longitude=resp_content["longitude"],
                zoom=scale_to_zoom(uid, resp_content["scale"]),
                place=resp_content["place"],
                description=resp_content["description"],
            )
        except (IntegrityError, ValueError):
            return HttpResponse(status=400)

        return JsonResponse(
            {
                "id": new_memory.id,
            }
        )

    user_info = get_user_info(uid)
    add_form = AddMemoryForm()
    m = create_map(uid)
    context = {
        "name": user_info["name"],
        "avatar": user_info["avatar"],
        "map": m._repr_html_(),
        "add_form": add_form,
    }
    return render(request, "map.html", context)
