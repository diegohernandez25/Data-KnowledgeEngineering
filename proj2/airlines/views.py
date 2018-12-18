import sys
#sys.path.append("..")
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
import json
import datasets.searchRoutes as sr
import datasets.querywikidata as qw
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render, redirect
from django.conf import settings
from os.path import join

#sys.path+=[join(settings.BASE_DIR,'')]
#import querywikidata as wiki

# Create your views here.

def index(request):
	if 'query_citymonument' in request.POST:
		print("QUERY_CITYMONUMENT")
		_city = request.POST['query_citymonument']
		_query =qw.queryIsCity(_city)
		print("queryIsCity: ",str(_query))
		_res =qw.queryData(_query,ask=True)
	#	if not _res:
	#		print("Not a city")
			#TODO: find cities with symilar name

		_query =qw.queryMonumentCities(_city)
		print("queryMonumentCities:",_query)
		_res =qw.queryData(_query)
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
	tparams['africa'] = listCountries('Africa')
	tparams['asia'] = listCountries('Asia')
	tparams['europe'] = listCountries('Europe')
	tparams['northame'] = listCountries('North America')
	tparams['oceania'] = listCountries('Oceania')
	tparams['southame'] = listCountries('South America')
	tparams['all_cont'] = tparams['africa'] + tparams['asia'] + tparams['europe'] + tparams['northame'] + tparams['oceania'] + tparams['southame']

	return render(request, 'index.html',tparams)

def getCities(request, country):
	resp = "<html><body>{}</body></html>".format(listCities(country))
	return HttpResponse(resp)

def getAirports(request, country):
	resp = "<html><body>{}</body></html>".format(listAirports(country))
	return HttpResponse(resp)

def listCountries(continent):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.countriesOfContinent(continent)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = []
	for c in results:
	    #print(c)
	    lst.append(c['label']['value'])
	return lst

def listCities(country):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.queryCountryAirports(country)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = []
	for c in results:
	    #print(c)
	    if c['citylabel']['value'] not in lst:
	        lst.append(c['citylabel']['value'])
	return lst

def listAirports(country):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.citysWithAirport(country)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = []
	for c in results:
	    #print(c)
	    lst.append(c['label']['value'])
	return lst
