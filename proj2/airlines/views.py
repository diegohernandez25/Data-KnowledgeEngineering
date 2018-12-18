from django.shortcuts import render
import json
import datasets.searchRoutes as sr
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

    return render(request, 'index.html',tparams)
