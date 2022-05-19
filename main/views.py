from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def auth(request):
    return render(request, 'welcome.html')
