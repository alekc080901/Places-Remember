from . import views
from .const import AUTH_URL

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path

urlpatterns = [
    path('', views.home, name="home"),
    path('welcome', views.welcome, name="welcome"),
    path(AUTH_URL, views.auth_confirm, name="auth"),
    path('logout', views.logout, name="logout"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico"), permanent=True),
    ),
    path('map', views.map_handle, name='map'),
]
