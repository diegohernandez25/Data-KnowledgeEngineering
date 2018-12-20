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
from datasets.converter import distancecoord


def index(request):
    repo_name, accessor = sr.connectGraphDB()

    processed_routes = []

    tparams = {}
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
    tail = "</body>\n</html>"
    cities = listCities(country)
    elems = ""
    for c in cities:
        elems += c['citylabel'] + "<br>\n"

    return HttpResponse(head + elems + tail)


def getCountryAirports(request, country):
    resp = "<html><body>{}</body></html>".format(listCountryAirports(country))
    return HttpResponse(resp)


def getCityAirports(request, city):
    head = "<html>\n<body>\n"
    tail = "</body>\n</html>"
    elems = getCityAirportsRdfa(city)
    return HttpResponse(head + elems + tail)


def getRoutes(request, src, dst, year, month, day):
    head = "<html>\n\t<body>\n"
    tail = "\t</body>\n</html>"
    routes = sr.routeFinderNAME(src, dst, str(year)+"-"+str(month)+"-"+str(day))
    elems = ""
    cnt = 0

    if routes==None:
        return HttpResponse('No routes found')

    for r in routes:
        div = "\n\t\t<div id=\"flight" + str(cnt) + "\" about=\"" + routes[r]['uri'] + "\">"
        elem = "\n\t\t\t<h2><b><span id=\"optimize" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/optimize\" style=\"text-transform: capitalize;\">" + r + "</span> optimization</b></h2>"
        elem += "\n\t\t\tRoute id: <span id=\"id" + str(cnt) + "\" property=\"http://airlinesdot.com/resource/route/id\">" + routes[r]['uri'][57:] + "</span><br>"
        elem += "\n\t\t\tCost: <span id=\"cost" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/cost\">" + str(
            routes[r]['cost']) + "</span><br>"
        elem += "\n\t\t\tPrice: <span id=\"price" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/price\">" + str(
            routes[r]['price']) + "</span>€<br>"
        elem += "\n\t\t\tDistance: <span id=\"distance" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/distance\">" + str(
            routes[r]['distance']) + "</span> km<br>"
        elem += "\n\t\t\tHops: <span id=\"hops" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/hops\">" + str(
            routes[r]['nrhops']) + "</span><br>"
        elem += "\n\t\t\tElapsed time: <span id=\"elapsed" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/time\">" + str(
            routes[r]['elapsedtimepretty']) + "</span><br>"
        if r != "flighttime":
            elem += "\n\t\t\tArrival: <span id=\"arrival" + str(cnt) + "\" property=\"http://www.airlinesdot.com/resource/route/time\">" + str(
            routes[r]['arrival']) + "</span><br>"

        elem += "\n\n\t\t\t<h3>Subroutes:</h3>"

        cnt_sub = 0
        for subr in routes[r]['route']:
            repo_name, accessor = sr.connectGraphDB()
            query = sr.getInfoRoute(subr)
            query_result = sr.queryGraphDB(query, accessor, repo_name)[0]

            sourceId = query_result['sourceId']
            destinationId = query_result['destinationId']

            query = sr.getAirportInfo(sourceId)
            source = sr.queryGraphDB(query, accessor, repo_name)[0]

            query = sr.getAirportInfo(destinationId)
            destination = sr.queryGraphDB(query, accessor, repo_name)[0]

            srcinfo = getSingleAirportRdfa2(source, cnt, cnt_sub, "src")
            dstinfo = getSingleAirportRdfa2(destination, cnt, cnt_sub, "dst")

            elem += "\n\n\t\t\t<div rel=\"http://www.airlinesdot.com/resource/route/subroute\">"

            elem += "\n\t\t\t\t<div about=\"" + subr + "\">"
            elem += "\n\t\t\t\t\tSubroute ID: <span id=\"subrouteId_r" + str(cnt) + "_sub" + str(cnt_sub) + "\" property=\"http://openflights.org/resource/route/id/\">" + subr[41:] + "</span><br>"
            elem += "\n\t\t\t\t\t<div rel=\"http://www.airlinesdot.com/resource/route/source\">"
            elem += "\n\t\t\t\t\t\t<div about=\"" + sourceId + "\">"
            elem += "\n\t\t\t\t\t\t\t<b>Source:<br></b>"

            for l in srcinfo.splitlines():
                elem += "\n\t\t\t\t\t\t\t" + l
            elem += "\n\t\t\t\t\t\t</div>"
            elem += "\n\t\t\t\t\t</div>"

            elem += "\n\t\t\t\t\t<div rel=\"http://www.airlinesdot.com/resource/route/destination\">"
            elem += "\n\t\t\t\t\t\t<div about=\"" + destinationId + "\">"

            elem += "\n\t\t\t\t\t\t\t<b>Destination:<br></b>"

            for l in dstinfo.splitlines():
                elem += "\n\t\t\t\t\t\t\t" + l

            elem += "\n\t\t\t\t\t\t</div>"
            elem += "\n\t\t\t\t\t</div>"
            elem += "\n\t\t\t\t</div>"
            elem += "\n\t\t\t</div><br>"
            cnt_sub += 1
        elem += "\n\t\t</div>\n"


        elems += div + elem
        cnt += 1


    return HttpResponse(head + elems + tail)


def getDestination(request, obj):
    resp = "<html><body>{}</body></html>".format(listDestinations(obj.replace("_", " ")))
    return HttpResponse(resp)


def getAirports(request, country):
    resp = "<html><body>{}</body></html>".format(listAirports(country))
    return HttpResponse(resp)


def getMonumentCoords(request, city):
    resp = "<html><body>{}</body></html>".format(listMonuments(city))
    return HttpResponse(resp)


def listCityCoords(city):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = qw.queryCityCoord(city)
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings']
    print("results", repr(results))
    coord = list()
    if results:
        coord = eval(results[0]['coord']['value'].replace("Point", "").replace(" ", ","))
        coord = [coord[0], coord[1]]
    return coord


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
        cord = eval(c['coords']['value'].replace("Point", "").replace(" ", ","))
        d['lat'] = cord[0]
        d['lon'] = cord[1]
        lat_mean += float(cord[0])
        lon_mean += float(cord[1])
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
		print(c)
		monuments = dict()
		monuments['label']= c['label']['value']
		monuments['typelabel'] = c['typelabel']['value']
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
    results = qw.queryData(query)
    lst = []
    for c in results:
        # print(c)
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
        print(" a is")
        print(a)
        div = "<div about=\"" + a['airport'] + "\">"
        elem = div + getSingleAirportRdfa(a)
        elems += elem + "</div>\n<p>\n"
    return elems

def getSingleAirportRdfa2(a, cnt, cnt_sub, tail):
    span = "<span "
    Open = " property=\""
    elem = "\nLabel: " + span + "id=\"label_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/label\">" + a[
        'label'] + "</span><br>"
    elem += "\nIATA: " + span + "id=\"iata_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/iata\">" + a['iata'] + "</span><br>"
    elem += "\nCountry: " + span + "id=\"country_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/country\">" + a[
        'country'] + "</span><br>"
    elem += "\nCity: " + span + "id=\"city_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/city\">" + a['city'] + "</span><br>"
    elem += "\nLongitude: " + span + "id=\"lon_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/longitude\">" + a[
        'airlon'] + "</span><br>"
    elem += "\nLatitude: " + span + "id=\"lat_r" + str(cnt) + "_sub" + str(cnt_sub) + "_" + tail + "\"" + Open + "http://openflights.org/resource/airport/latitudel\">" + a[
        'airlat'] + "</span>\n"

    return elem

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
        'airlat'] + "</span>\n"

    return elem

def findBestAirport(local):
	repo_name, accessor = sr.connectGraphDB()
	query = qw.queryCountryOf(local)
	results = qw.queryData(query)
	if(not len(results) or not results[0].get('country')):
		return None,None
	country=results[0]['country']['value']

	local_coods = eval(results[0]['coords']['value'].replace("Point","").replace(" ",","))
	local_coods=(float(local_coods[1]),float(local_coods[0]))

	query = sr.getAirportsFromCountry(country)
	query_result = sr.queryGraphDB(query, accessor, repo_name)

	query_result.sort(key=lambda x:distancecoord((float(x['lat']),float(x['lon'])),local_coods))
	if(not len(query_result)):
		return None, None
	return query_result[0],list(local_coods)

def getCityCoords(request, orig, dest, date):
    repo_name, accessor = sr.connectGraphDB()
    bestroute, origincoord, destinycoord = smartAirRoute(orig, dest, date)
    d = dict()
    d['orig'] = [origincoord[1], origincoord[0]]
    d['dest'] = [destinycoord[0], destinycoord[1]]
    print("bestroute: ", repr(bestroute))
    if bestroute:
        d['hop'] = dict()
        d['hop']['route'] = list()
        for h in bestroute['hop']['route']:
            query = sr.getInfoRoute(h)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['sourceId'])
            res1 = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['destinationId'])
            res2 = sr.queryGraphDB(query, accessor, repo_name)
            node = dict()
            node['origin_air'] = query_result[0]['sourceIdLabel']
            node['destination_air'] = query_result[0]['destinationIdLabel']
            node['destination'] = query_result[0]['destination']
            node['source'] = query_result[0]['source']
            node['lat1'] = float(res1[0]['airlat'])
            node['lon1'] = float(res1[0]['airlon'])
            node['lat2'] = float(res2[0]['airlat'])
            node['lon2'] = float(res2[0]['airlon'])
            d['hop']['route'].append(node)
        d['hop']['price'] = bestroute['hop']['price']
        d['hop']['cost'] = bestroute['hop']['cost']
        d['hop']['distance'] = bestroute['hop']['distance']
        d['hop']['time'] = bestroute['hop']['elapsedtimepretty']

        d['price'] = dict()
        d['price']['route'] = list()
        for h in bestroute['price']['route']:
            query = sr.getInfoRoute(h)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['sourceId'])
            res1 = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['destinationId'])
            res2 = sr.queryGraphDB(query, accessor, repo_name)
            node = dict()
            node['origin_air'] = query_result[0]['sourceIdLabel']
            node['destination_air'] = query_result[0]['destinationIdLabel']
            node['destination'] = query_result[0]['destination']
            node['source'] = query_result[0]['source']
            node['lat1'] = float(res1[0]['airlat'])
            node['lon1'] = float(res1[0]['airlon'])
            node['lat2'] = float(res2[0]['airlat'])
            node['lon2'] = float(res2[0]['airlon'])
            d['price']['route'].append(node)
        d['price']['price'] = bestroute['price']['price']
        d['price']['cost'] = bestroute['price']['cost']
        d['price']['distance'] = bestroute['price']['distance']
        d['price']['time'] = bestroute['price']['elapsedtimepretty']

        d['distance'] = dict()
        d['distance']['route'] = list()
        for h in bestroute['distance']['route']:
            query = sr.getInfoRoute(h)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['sourceId'])
            res1 = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['destinationId'])
            res2 = sr.queryGraphDB(query, accessor, repo_name)
            node = dict()
            node['origin_air'] = query_result[0]['sourceIdLabel']
            node['destination_air'] = query_result[0]['destinationIdLabel']
            node['destination'] = query_result[0]['destination']
            node['source'] = query_result[0]['source']
            node['lat1'] = float(res1[0]['airlat'])
            node['lon1'] = float(res1[0]['airlon'])
            node['lat2'] = float(res2[0]['airlat'])
            node['lon2'] = float(res2[0]['airlon'])
            d['distance']['route'].append(node)

        d['distance']['price'] = bestroute['distance']['price']
        d['distance']['cost'] = bestroute['distance']['cost']
        d['distance']['distance'] = bestroute['distance']['distance']
        d['distance']['time'] = bestroute['distance']['elapsedtimepretty']

        d['time'] = dict()

        d['time']['route'] = list()
        for h in bestroute['time']['route']:
            query = sr.getInfoRoute(h)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['sourceId'])
            res1 = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['destinationId'])
            res2 = sr.queryGraphDB(query, accessor, repo_name)
            node = dict()
            node['origin_air'] = query_result[0]['sourceIdLabel']
            node['destination_air'] = query_result[0]['destinationIdLabel']
            node['destination'] = query_result[0]['destination']
            node['source'] = query_result[0]['source']
            node['lat1'] = float(res1[0]['airlat'])
            node['lon1'] = float(res1[0]['airlon'])
            node['lat2'] = float(res2[0]['airlat'])
            node['lon2'] = float(res2[0]['airlon'])
            d['time']['route'].append(node)

        d['time']['price'] = bestroute['time']['price']
        d['time']['cost'] = bestroute['time']['cost']
        d['time']['distance'] = bestroute['time']['distance']
        d['time']['time'] = bestroute['time']['elapsedtimepretty']

        d['flighttime'] = dict()
        d['flighttime']['route'] = list()
        for h in bestroute['flighttime']['route']:
            query = sr.getInfoRoute(h)
            query_result = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['sourceId'])
            res1 = sr.queryGraphDB(query, accessor, repo_name)
            query = sr.getAirportCoords(query_result[0]['destinationId'])
            res2 = sr.queryGraphDB(query, accessor, repo_name)
            node = dict()
            node['origin_air'] = query_result[0]['sourceIdLabel']
            node['destination_air'] = query_result[0]['destinationIdLabel']
            node['destination'] = query_result[0]['destination']
            node['source'] = query_result[0]['source']
            node['lat1'] = float(res1[0]['airlat'])
            node['lon1'] = float(res1[0]['airlon'])
            node['lat2'] = float(res2[0]['airlat'])
            node['lon2'] = float(res2[0]['airlon'])
            d['flighttime']['route'].append(node)

        d['flighttime']['price'] = bestroute['flighttime']['price']
        d['flighttime']['cost'] = bestroute['flighttime']['cost']
        d['flighttime']['distance'] = bestroute['flighttime']['distance']
        d['flighttime']['time'] = bestroute['flighttime']['elapsedtimepretty']

    d = json.dumps(d)
    print("d: ", d)
    resp = "<html><body>{}</body></html>".format(d)
    return HttpResponse(resp)

def smartAirRoute(localA,localB,date):
	a,locala=findBestAirport(localA)
	b,localb=findBestAirport(localB)
	if a!=None:
		_a=[locala,[float(a['lat']),float(a['lon'])]]
	else:
		_a=[None,None]
	if b !=None:
		_b=[localb,[float(b['lat']),float(b['lon'])]]
	else:
		_b=[None,None]
	bestroute=sr.routeFinderURI(a['airport'],b['airport'],date) if a!=None and b!=None else None
	return bestroute,_a,_b



