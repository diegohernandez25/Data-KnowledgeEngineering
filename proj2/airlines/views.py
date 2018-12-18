import sys
# sys.path.append("..")
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
import json
import datasets.searchRoutes as sr
import datasets.querywikidata as qw
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render, redirect
from django.conf import settings
from os.path import join


# sys.path+=[join(settings.BASE_DIR,'')]
# import querywikidata as wiki

# Create your views here.

def index(request):
    if 'query_citymonument' in request.POST:
        print("QUERY_CITYMONUMENT")
        _city = request.POST['query_citymonument']
        _query = qw.queryIsCity(_city)
        print("queryIsCity: ", str(_query))
        _res = qw.queryData(_query, ask=True)
        #	if not _res:
        #		print("Not a city")
        # TODO: find cities with symilar name

        _query = qw.queryMonumentCities(_city)
        print("queryMonumentCities:", _query)
        _res = qw.queryData(_query)
        print(_res)
        tparams = dict()
        tparams["monuments"] = list()
        keys = {"labels", "coords"}
        tparams["info"] = True if len(_res) > 0 else False
        stored = list()
        for e in _res:
            if e.get("label") and e.get("coords"):
                if e["label"]["value"] not in stored:
                    stored.append(e["label"]["value"])
                    _coords = eval(e["coords"]["value"].replace("Point", "").replace(" ", ","))
                    _lat = _coords[0]
                    print(_lat)
                    _lon = _coords[1]
                    print(_lon)
                    # tparams["monuments"].append({'name':e["label"]["value"],'lat':_lat,'lon':_lon})
                    tparams["monuments"].append({'name': e["label"]["value"], 'coords': _coords})
        print("tparams: ", repr(tparams))
        return render(request, 'index.html', tparams)

    repo_name, accessor = sr.connectGraphDB()
    print("before")
    print(listCities('Portugal'))
    query = sr.getAirportCity("Lisbon")
    query_result = sr.queryGraphDB(query, accessor, repo_name)[0]
    airport_coords = [query_result['airlat'], query_result['airlon']]
    airport_uri = query_result['airport']
    fields = [float(airport_coords[0]), float(airport_coords[1]), int(airport_uri[43:]), "Aeroporto de Lisboa"]
    query = sr.getRoutesAirport(airport_uri)
    routes = sr.queryGraphDB(query, accessor, repo_name)

    processed_routes = []

    for r in range(1, len(routes)):
        route = routes[r]
        current = [int(route['route'][41:])] + fields + ["info about Lisbon airport"]
        curr_uri = route['airportend']
        curr_coords = [route['airlat'], route['airlon']]
        current = current + [float(curr_coords[0]), float(curr_coords[1]), int(curr_uri[43:]),
                             "Airport " + curr_uri[43:], "info about this airport"]
        processed_routes.append(tuple(current))

    # print(processed_routes)
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
    tparams['all_cont'] = tparams['africa'] + tparams['asia'] + tparams['europe'] + tparams['northame'] + tparams[
        'oceania'] + tparams['southame']

    return render(request, 'index.html', tparams)


def getCities(request, country):
    head = "<html>\n<body>\n"
    tail ="</body>\n</html>"
    cities = listCities(country)
    elems=""
    for c in cities:
        elems += c['citylabel'] + "<br>\n"

    return HttpResponse(head+elems+tail)


def getCountryAirports(request, country):
    resp = "<html><body>{}</body></html>".format(listCountryAirports(country))
    return HttpResponse(resp)

def getCityAirports(request, city):
    head = "<html>\n<body>\n"
    tail ="</body>\n</html>"
    elems = getCityAirportsRdfa(city)
    return HttpResponse(head + elems + tail)

def getRoutes(request, src, dst):
    head = "<html>\n<body>\n"
    tail ="</body>\n</html>"
    routes = sr.routeFinderNAME(src, dst)
    elems = ""
    for r in routes:
        #div = "<div about=\"" + str(routes[r]['route']) + "\">"
        elem = "\nOptimized for: <span property=\"http://www.airlinesdot.com/resource/route/optimize\">"+ r + "</span><br>"
        elem += "\nCost: <span property=\"http://www.airlinesdot.com/resource/route/cost\">" + str(routes[r]['cost']) + "</span><br>"
        elem += "\nPrice for: <span property=\"http://www.airlinesdot.com/resource/route/price\">"+ str(routes[r]['price']) + "</span><br>"
        elem += "\nDistance: <span property=\"http://www.airlinesdot.com/resource/route/distance\">" + str(routes[r]['distance']) + "</span><br>"
        elem += "\nHops: <span property=\"http://www.airlinesdot.com/resource/route/hops\">" + str(routes[r]['nrhops']) + "</span><br>"
        elem += "\nElapsed time: <span property=\"http://www.airlinesdot.com/resource/route/time\">" + str(routes[r]['elapsedtime']) + "</span><br>"


        elem += "\n<br>Subroutes:\n<br>Source:<br>"
        for subr in routes[r]['route']:
            repo_name, accessor = sr.connectGraphDB()
            query = sr.getRoutesAirport(subr)
            print(query)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            print(query_result)
            source = query_result['sourceId']
            destination = query_result['destinationId']

            srcinfo = getSingleAirportRdfa(source)
            dstinfo = getSingleAirportRdfa(destination)
            elem += srcinfo
            elem += "\n<br>Destination:"
            elem += dstinfo

        elems += elem
    return HttpResponse(head + elems + tail)


def listCountries(continent):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = qw.countriesOfContinent(continent)
    results = qw.queryData(query)
    lst = []
    for c in results:
        # print(c)
        lst.append(c['label']['value'])
    return lst


def listCitiesWD(country):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = qw.queryCountryAirports(country)
    results = qw.queryData(query)
    lst = []
    for c in results:
        # print(c)
        if c['citylabel']['value'] not in lst:
            lst.append(c['citylabel']['value'])
    return lst


def listCountryAirports(country):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = qw.citysWithAirport(country)
    results = qw.queryData(query)
    lst = []
    for c in results:
        # print(c)
        lst.append(c['label']['value'])
    return lst

def listCityAirports(city):
    repo_name, accessor = sr.connectGraphDB()
    query = sr.getAirportCity(city)
    query_result = sr.queryGraphDB(query, accessor, repo_name)
    return query_result

def listCities(country):
    repo_name, accessor = sr.connectGraphDB()
    query = sr.getCitysWithAirports(country)
    query_result = sr.queryGraphDB(query, accessor, repo_name)
    return query_result

def getCityAirportsRdfa(city):
    airports = listCityAirports(city)
    elems = ""
    for a in airports:
        div = "<div about=\"" + a['airport'] + "\">"
        elem = div + getSingleAirportRdfa(a)
        elems += elem
    return elems

def getSingleAirportRdfa(a):
    spanOpen = "<span property=\""
    elem = "\nLabel: " + spanOpen + "http://openflights.org/resource/airport/label\">" + a[
        'label'] + "</span><br>"
    elem += "\nIATA: " + spanOpen + "http://openflights.org/resource/airport/iata\">" + a['iata'] + "</span><br>"
    elem += "\nCountry: " + spanOpen + "http://openflights.org/resource/airport/country\">" + a[
        'country'] + "</span><br>"
    elem += "\nCity: " + spanOpen + "http://openflights.org/resource/airport/city\">" + a['city'] + "</span><br>"
    elem += "\nLongitude: " + spanOpen + "http://openflights.org/resource/airport/longitude\">" + a[
        'airlon'] + "</span><br>"
    elem += "\nLatitude: " + spanOpen + "http://openflights.org/resource/airport/latitudel\">" + a[
        'airlat'] + "</span>\n</div>\n<p>\n"

    return elem