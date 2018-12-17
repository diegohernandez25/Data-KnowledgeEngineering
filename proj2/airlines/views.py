from django.shortcuts import render
import json
import datasets.searchRoutes as sr
# Create your views here.


def index(request):
    #sr.search_path("Lisbon", "Porto", 10)
    endpoint,repo_name,client,accessor = sr.connectGraphDB()
    query = sr.getAirportCity("Lisbon")
    airport_uri = sr.queryGraphDB(query,accessor,repo_name)['results']['bindings'][0]['airport']['value']
    query = sr.getAirportCoord(airport_uri)
    airport_coords = sr.queryGraphDB(query,accessor,repo_name)['results']['bindings'][0]
    fields = [float(airport_coords['lat']['value']), float(airport_coords['lon']['value']), int(airport_uri[43:]), "Aeroporto de Lisboa"]
    query = sr.getRoutesAirport(airport_uri)
    routes = sr.queryGraphDB(query,accessor,repo_name)['results']['bindings']

    processed_routes = []

    for r in range(1,len(routes)):
        current = [r] + fields + ["info about Lisbon airport"]
        curr_uri = routes[r]['airportend']['value']
        query = sr.getAirportCoord(curr_uri)
        curr_coords = sr.queryGraphDB(query,accessor,repo_name)['results']['bindings'][0]
        current = current + [float(curr_coords['lat']['value']), float(curr_coords['lon']['value']), int(curr_uri[43:]), "Airport " + curr_uri[43:], "info about this airport"]
        processed_routes.append(tuple(current))

    print(processed_routes)

    tparams = {}
    info = "Airport details"
    # (route, src_lat, src_long, src_iata, src_name, src_info, dst_lat, dst_long, dst_iata, dst_name, dst_info)
    tparams['route'] = processed_routes

    return render(request, 'index.html',tparams)
