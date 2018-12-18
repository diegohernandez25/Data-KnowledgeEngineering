import sys
sys.path.append("..")
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
import json
import datasets.searchRoutes as sr
from django.shortcuts import render, redirect
from django.conf import settings
from os.path import join

sys.path+=[join(settings.BASE_DIR,'')]
import querywikidata as wiki

# Create your views here.

def index(request):
	assert isinstance(request,HttpRequest)
	if 'query_citymonument' in request.POST:
		print("QUERY_CITYMONUMENT")
		_city = request.POST['query_citymonument']
		_query = wiki.queryIsCity(_city)
		print("queryIsCity: ",str(_query))
		_res = wiki.queryData(_query,ask=True)
	#	if not _res:
	#		print("Not a city")
			#TODO: find cities with symilar name
			 
		_query = wiki.queryMonumentCities(_city)
		print("queryMonumentCities:",_query)
		_res = wiki.queryData(_query)
		print(_res)	
		tparams = dict()
		tparams["monuments"]=list()
		keys={"labels","coords"}
		tparams["info"] = True if len(_res)>0 else False
		stored= list()
		for e in _res:
			if e.get("label") and e.get("coords"):
				if e["label"]["value"] not in stored:
					stored.append(e["label"]["value"])
					_coords= eval(e["coords"]["value"].replace("Point","").replace(" ",","))
					_lat=_coords[0]
					print(_lat)
					_lon=_coords[1]
					print(_lon)
					#tparams["monuments"].append({'name':e["label"]["value"],'lat':_lat,'lon':_lon})
					tparams["monuments"].append({'name':e["label"]["value"],'coords':_coords})
		print("tparams: ",repr(tparams))
		return render(request, 'index.html', tparams)

	repo_name,accessor = sr.connectGraphDB()
	query = sr.getAirportCity("Lisbon")
	query_result = sr.queryGraphDB(query,accessor,repo_name)[0]
	airport_coords = [query_result['airlat'], query_result['airlon']]
	airport_uri = query_result['airport']
	fields = [float(airport_coords[0]), float(airport_coords[1]), int(airport_uri[43:]), "Aeroporto de Lisboa"]
	query = sr.getRoutesAirport(airport_uri)
	routes = sr.queryGraphDB(query,accessor,repo_name)

	processed_routes = []

	for r in range(1,len(routes)):
	    route = routes[r]
	    current = [int(route['route'][41:])] + fields + ["info about Lisbon airport"]
	    curr_uri = route['airportend']
	    curr_coords = [route['airlat'], route['airlon']]
	    current = current + [float(curr_coords[0]), float(curr_coords[1]), int(curr_uri[43:]), "Airport " + curr_uri[43:], "info about this airport"]
	    processed_routes.append(tuple(current))

	#print(processed_routes)

	tparams = {}
	info = "Airport details"
	# (route, src_lat, src_long, src_iata, src_name, src_info, dst_lat, dst_long, dst_iata, dst_name, dst_info)
	tparams['route'] = processed_routes

	return render(request, 'index.html',tparams)



