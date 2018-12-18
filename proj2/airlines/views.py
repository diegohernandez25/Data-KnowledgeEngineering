from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import datasets.searchRoutes as sr
import datasets.querywikidata as qw
from SPARQLWrapper import SPARQLWrapper, JSON
# Create your views here.


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

