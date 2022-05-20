from . import views

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path

urlpatterns = [
    path('', views.home, name="home"),
    path('welcome', views.auth, name="welcome"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico"), permanent=True),
    ),
]