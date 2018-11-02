from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
# Create your views here.

import stubs.uaservices as ua
import datetime

def index(request):
    return render(request, 'index.html',{})

    request.build_absolute_uri

def news(request):
    # assert isinstance(request, HttpRequest)
    news = ua.UANews()
    news.get()
    tparams = {}
    tparams['all_news'] = list(news.news.values())
    return render(request,'news.html',tparams)
    #return HttpRequest.build_absolute_uri('news.html')

def weather(request):
    weather = ua.WeatherService()
    weather.get()
    tparams = {}

    for i in range(0, 3):
        weekday = 'weekday' + str(i + 1)
        status = 'status' + str(i + 1)
        mintemp = 'mintemp' + str(i + 1)
        maxtemp = 'maxtemp' + str(i + 1)
        humidity = 'humidity' + str(i + 1)
        date = 'date' + str(i + 1)
        img = 'img' + str(i + 1)

        current_date = datetime.date.today() + datetime.timedelta(days=i)
        weather_img = ""
        weather_val = weather.weather[i]['Status']

        if 'Minimum Temperature' in weather.weather[i].keys():
            tparams.update({mintemp: weather.weather[i]['Minimum Temperature']})
        else:
            tparams.update({mintemp: "--"})
        if 'Maximum Temperature' in weather.weather[i].keys():
            tparams.update({maxtemp: weather.weather[i]['Maximum Temperature']})
        else:
            tparams.update({maxtemp: "--"})

        if weather_val == "Light Rain" or weather_val == "Drizzle" or weather_val == "Rainy" or weather_val == "Heavy Rain" or weather_val == "Heavy Rain Showers" or weather_val == "Light Rain Showers":
            weather_img = "/static/img/weather-rainy.svg"
        elif weather_val == "Sunny" or weather_val == "Sunny Intervals" or weather_val == "Clear Sky":
            weather_img = "/static/img/weather-sunny.svg"
        elif weather_val == "Light Cloud" or weather_val == "Partly Cloudy":
            weather_img = "/static/img/weather-partlycloudy.svg"
        elif weather_val == "Thundery Showers":
            weather_img = "/static/img/weather-lightning-rainy.svg"
        elif weather_val == "Light Snow" or weather_val == "Light Snow Showers":
            weather_img = "/static/img/weather-snowy.svg"
        elif weather_val == "Sleet Showers":
            weather_img = "/static/img/weather-hail.svg"
        else:
            weather_img = "/static/img/weather-cloudy.svg"

        tparams.update({
            date: current_date.strftime("%B %d"),
            weekday: weather.weather[i]['Weekday'],
            status: weather_val,
            humidity: weather.weather[i]['Humidity'],
            img: weather_img
        })

    return render(request, 'weather.html', tparams)

def schedule(request):
    return render(request,'schedule.html',{})

def room(request):
    return render(request,'room.html',{})

def canteen(request):
    return render(request,'canteen.html',{})

def parkinglot(request):
    parking = ua.UAParking()
    parking.get()
    tparams = {}
    tparams['all_parkings'] = list(parking.parking.values())

    return render(request,'parkinglot.html',tparams)
