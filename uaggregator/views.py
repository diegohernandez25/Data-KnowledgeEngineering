from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
# Create your views here.

import stubs.uaservices as ua
import datetime
import sys 

from os.path import join
from django.conf import settings



sys.path+=[join(settings.BASE_DIR,'stubs/horarios')]
import stubs.horarios.horario as horario



def index(request):
    return render(request, 'index.html',{})

    request.build_absolute_uri

def news(request):
	assert isinstance(request, HttpRequest)
	news = ua.UANews()
	news.get()
	tparams = {}
		
	if 'init_date' in request.POST or 'final_date' in request.POST and 'num' in request.POST:
		print("This is a POST")
		_init_date = request.POST['init_date']
		_final_date = request.POST['final_date']
		_num = request.POST['num']
		if(not validate_date(_init_date)): _init_date=None
		if(not validate_date(_final_date)): _final_date=None
		news.specific_fetch(None,_num,_init_date,_final_date,None,1,11)	
			
	tparams['all_news'] = list(news.news.values())
	print(tparams['all_news'])
	return render(request,'news.html',tparams)
	#return HttpRequest.build_absolute_uri('news.html')

def validate_date(date):
	print(date)
	try:
		datetime.datetime.strptime(date,'%d-%m-%Y')
	except ValueError:
		print("Incorrect data format, should be dd-mm-yyyy")
		#raise ValueError("Incorrect data format, should be dd-mm-yyyy")
		return False
	return True

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
            img: weather_img, 
        })

    return render(request, 'weather.html', tparams)

def schedule(request):
	assert isinstance(request, HttpRequest)
	tparams = {}
	if 'curso' in request.POST and 'ano' in request.POST:
		_ano=int(request.POST['ano'])
		_curso=int(request.POST['curso'])
		_schedule = ua.ScheduleMaker(horario.gerar_horarios(_curso,_ano))
		_schedule.get()
		tparams['all_schedules'] = _schedule.schedules	
		
	return render(request,'schedule.html',tparams)

def room(request):
	assert isinstance(request, HttpRequest)
	tparams= dict()
	tparams['all_rooms']=list()
	tparams['reserved']=False
	if 'data' in request.POST and 'appt-time' in request.POST and 'appt-time-last' in request.POST:
		_data = request.POST['data']
		_init_date = request.POST['appt-time']
		_final_date = request.POST['appt-time-last']
		_salas = horario.listar_salas_livres(_init_date,_final_date,_data)
		
		request.session['data'] = _data
		request.session['init_date'] = _init_date
		request.session['final_date'] = _final_date
		
		tparams['all_rooms']+= horario.listar_salas_livres(_init_date,_final_date,_data)
		tparams['info']={'data':_data, 'init_date':_init_date, 'final_date':_final_date}
	
	elif 'nmec' in request.POST:
		_nmec=request.POST['nmec']
		_choice=request.POST['choice']
		print(request.session['final_date'])
		print(request.session['data'])
		if(horario.reservar_sala(_nmec,_choice,request.session['init_date'],request.session['final_date'],request.session['data'])):
			tparams['reserved']=True
			#if request.session['all_reservas']==None:
			#	request.session['all_reservas'])=list()
			#request.session['all_reservas'].append({'sala':request.session['init_date']})
		
	return render(request,'room.html',tparams)
"""
def add_index(_list):
	tmp_l=list()
	for i in range(0,len(_list)):
		tmp_l.append(i,_list[i])
	print tmp_l
	return tmp_l
"""

def canteen(request):
	assert isinstance(request, HttpRequest)
	_sas = ua.SASService()
	_sas.get()
	tparams = {}
	tparams['all_lunch'] = list(_sas.lunch.values())
	tparams['all_dinner'] = list(_sas.dinner.values())
	print(tparams)
	return render(request,'canteen.html',tparams)


def sac(request):
	assert isinstance(request, HttpRequest)
	_sac = ua.SACService()
	_sac.get()
	tparams = {}
	tparams['all_sac'] = list(_sac.tickets.values())
	return render(request,'sac.html',tparams)

def parkinglot(request):
    parking = ua.UAParking()
    parking.get()
    tparams = {}
    tparams['all_parkings'] = list(parking.parking.values())

    return render(request,'parkinglot.html',tparams)
