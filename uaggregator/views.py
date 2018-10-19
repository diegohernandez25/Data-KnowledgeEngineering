from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
# Create your views here.


def index(request):
    return render(request, 'index.html',{})

    request.build_absolute_uri

def news(request):
    return render(request,'news.html',{})
    #return HttpRequest.build_absolute_uri('news.html')

def meteorology(request):
    return render(request,'meteorology.html',{})

def schedule(request):
    return render(request,'schedule.html',{})

def room(request):
    return render(request,'room.html',{})

def cantine(request):
    return render(request,'cantine.html',{})

def parkinglot(request):
    return render(request,'parkinglot.html',{})
