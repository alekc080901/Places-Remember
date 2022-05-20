from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {'location_list': [1]})


def auth(request):
    return render(request, 'welcome.html')
