import sys
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
import json
import datasets.searchRoutes as sr
import datasets.querywikidata as qw
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render, redirect
from django.conf import settings
from os.path import join
import json

def index(request):

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


	tparams = {}
	info = "Airport details"
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

def getDestination(request, obj):
	print("def getDestination(request, obj):")
	resp = "<html><body>{}</body></html>".format(listDestinations(obj.replace("_"," ")))
	return HttpResponse(resp)

def getAirports(request, country):
	resp = "<html><body>{}</body></html>".format(listAirports(country))
	return HttpResponse(resp)

def getMonumentCoords(request, city):
	resp = "<html><body>{}</body></html>".format(listMonuments(city))
	return HttpResponse(resp)

def listDestinations(obj):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.queryProxCoord(obj)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = list()
	lat_mean = 0
	lon_mean = 0
	for c in results:
		d = dict()
		d['typelabel'] = c['typelabel']['value']
		d['itemlabel'] = c['itemlabel']['value']
		cord = eval(c['coords']['value'].replace("Point","").replace(" ",","))
		d['lat'] = cord[0]
		d['lon'] = cord[1]
		lat_mean+= float(cord[0])
		lon_mean+= float(cord[1])
		lst.append(d)
	lat_mean = lat_mean / len(results)
	lon_mean = lon_mean / len(results)
	obj = dict()
	obj['obj'] = lst
	obj['lat_mean'] = lat_mean
	obj['lon_mean'] = lon_mean
	return json.dumps(obj)


def listMonuments(city):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.queryMonumentCities(city)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = list()
	lat_mean = 0
	lon_mean = 0
	for c in results:
		monuments = dict()
		monuments['label']= c['label']['value']
		c = eval(c["coords"]["value"].replace("Point","").replace(" ",","))
		monuments['lat']= c[0]
		monuments['lon']= c[1]
		lat_mean+=float(c[0])
		lon_mean+=float(c[1])
		lst.append(monuments)
	lat_mean= lat_mean/ len(results)
	lon_mean= lon_mean/ len(results)
	monu = dict()
	monu['monuments'] = lst
	monu['lat_mean'] = lat_mean
	monu['lon_mean'] = lon_mean
	return json.dumps(monu)


def listCountries(continent):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	query = qw.countriesOfContinent(continent)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()['results']['bindings']
	lst = []
	for c in results:
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
	    lst.append(c['label']['value'])
	return lst
