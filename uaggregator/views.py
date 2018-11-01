from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
# Create your views here.

import stubs.uaservices as ua

def index(request):
    return render(request, 'index.html',{})

    request.build_absolute_uri

def news(request):
    # assert isinstance(request, HttpRequest)
    news = ua.UANews()
    news.get()
    tparams = {}
    #print(news.news)
    #for k,v in news.news:
    tparams['all_news'] = list(news.news.values())
    return render(request,'news.html',tparams)
    #return HttpRequest.build_absolute_uri('news.html')

def meteorology(request):
    weather = ua.WeatherService()
    weather.get()
    tparams = {}

    for i in range(0, 3):
        weekday = 'weekday' + str(i + 1)
        status = 'status' + str(i + 1)
        mintemp = 'mintemp' + str(i + 1)
        maxtemp = 'maxtemp' + str(i + 1)
        humidity = 'humidity' + str(i + 1)

        print(weather.weather[i].keys())
        if 'Minimum Temperature' in weather.weather[i].keys():
            tparams.update({mintemp: weather.weather[i]['Minimum Temperature']})
        if 'Maximum Temperature' in weather.weather[i].keys():
            tparams.update({maxtemp: weather.weather[i]['Maximum Temperature']})

        tparams.update( {
            weekday: weather.weather[i]['Weekday'],
            status: weather.weather[i]['Status'],
            humidity: weather.weather[i]['Humidity']
        })

    return render(request,'meteorology.html', tparams)

def schedule(request):
    return render(request,'schedule.html',{})

def room(request):
    return render(request,'room.html',{})

def cantine(request):
    return render(request,'cantine.html',{})

def parkinglot(request):
    return render(request,'parkinglot.html',{})
