import rdflib
from rdflib.namespace import RDF
import random
import math

base_uri='http://www.airlinesdot.com/resource/'

def parse():
	_graph = rdflib.ConjunctiveGraph()
	#_graph.parse("less_airroutes.ttl", format="n3")
	_graph.parse("airroutes.ttl", format="n3")
	return _graph

def getairlines(graph):
	return graph.query("""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
	PREFIX of: <http://openflights.org/resource/> 
	PREFIX pair: <http://openflights.org/resource/airline/> 
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 

	CONSTRUCT{
		?airline a of:Airline.
		?airline pair:callsign ?callsgn.
		?airline pair:country ?country.
		?airline pair:iata ?iata.
		?airline pair:icao ?icao.
		?airline rdfs:label ?name.
	}
	WHERE {
		?airline a of:Airline.
		?airline pair:active "Y".
		?airline pair:callsign ?callsgn.
		?airline pair:country ?country.
		?airline pair:iata ?iata.
		?airline rdfs:label ?name.
		OPTIONAL{
			?airline pair:icao ?icao.
		}
	}
	""").graph

def getuniqueIDs(graph):
	return graph.query("""
		SELECT distinct ?id 
		WHERE{
			 ?id ?pred ?obj.
		}
	""")

def genairlinedata(graph):

	#get all unique airlinesIDs
	airline_dict=dict()
	for airline in getuniqueIDs(graph):
		airline_dict[airline[0]]=dict()

	for key in airline_dict: #TODO GET MORE ACCURATE DATA, AVISAR DIEGO
		airline_dict[key]['costperdistance']=random.randint(10,20) #euro/hundredKm
		airline_dict[key]['basecost']=random.randint(10,50) #euro
		
	return airline_dict

def getairports(graph):
	return graph.query("""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
	PREFIX of: <http://openflights.org/resource/> 
	PREFIX port: <http://openflights.org/resource/airport/> 
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 

	CONSTRUCT{
		?airport a of:Airport.
		?airport port:altitude ?alt.
		?airport port:city ?city.
		?airport port:country ?country.
		?airport port:dst ?dst.
		?airport port:iata ?iata.
		?airport port:latitude ?lat.      
		?airport port:longitude ?lon.     
		?airport port:timezone ?timezone.
		?airport port:tz ?tz.
		?airport rdfs:label ?name.
	}
	WHERE {
		?airport a of:Airport.
		?airport port:altitude ?alt.
		?airport port:city ?city.
		?airport port:country ?country.
		?airport port:dst ?dst.
		?airport port:iata ?iata.
		?airport port:latitide ?lat.     #Typo here
		?airport port:longtitude ?lon.   #Typo here
		?airport port:timezone ?timezone.
		?airport port:tz ?tz.
		?airport rdfs:label ?name.
	}
	""").graph

def getroutes(graph):
	return graph.query("""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
	PREFIX route: <http://openflights.org/resource/route/>

    CONSTRUCT{
        ?sub ?pred ?obj.
    }
    WHERE {
        ?sub a of:Route.
        ?sub ?pred ?obj.
    	FILTER(?pred!=route:stops)
    }
	""").graph

def airportCoord(graph,airportID):
	latPred=rdflib.URIRef('http://openflights.org/resource/airport/latitude')
	lonPred=rdflib.URIRef('http://openflights.org/resource/airport/longitude')
	return (list(graph.objects(airportID,latPred))[0].toPython(),list(graph.objects(airportID,lonPred))[0].toPython())

	

def distancecoord(coorA,coorB): #in kilometers
#Haversine function
#https://www.movable-type.co.uk/scripts/latlong.html
	earth_radius=6371 #kms	

	phi1=math.radians(coorA[0])
	phi2=math.radians(coorB[0])

	deltaphi=math.radians(coorB[0]-coorA[0])
	deltalambda=math.radians(coorB[1]-coorA[1])

	a=math.sin(deltaphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(deltalambda/2)**2

	c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

	return earth_radius*c


def getroutesdata(routes,airports,airlines_data):
	srcAirportPred=rdflib.URIRef('http://openflights.org/resource/route/sourceId')
	dstAirportPred=rdflib.URIRef('http://openflights.org/resource/route/destinationId')
	airlinePred=rdflib.URIRef('http://openflights.org/resource/route/airlineId')
	print()
	for route in getuniqueIDs(routes):
		print(route[0])
		randTime=(random.randint(0,23),random.randint(0,59))
		randdow=random.choice(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
		tmpSpeed=random.randint(740,930) #average airplane airspeed


		print('src:',list(routes.objects(route[0],srcAirportPred)))
		print('dst:',list(routes.objects(route[0],dstAirportPred)))
		srcCoord=airportCoord(airports,list(routes.objects(route[0],srcAirportPred))[0])
		dstCoord=airportCoord(airports,list(routes.objects(route[0],dstAirportPred))[0])

		distance=distancecoord(srcCoord,dstCoord)
		duration=distance/tmpSpeed
		#duration=(duration/60 #TODO CALC DURATION

		print('air:',list(routes.objects(route[0],airlinePred)))
		airline_data=airlines_data[list(routes.objects(route[0],airlinePred))[0]]
		cost=airline_data['basecost']+airline_data['costperdistance']*distance/100

		print('randTime:',randTime)
		print('randdow:',randdow)
		print('tmpSpeed:',tmpSpeed)
		print('distance:',distance)
		print('duration:',duration)
		print('cost:',cost)
		print()
		

		

def main():
	finalRDF=rdflib.ConjunctiveGraph()
	print('Parsing airroutes.ttl, it might take while...')
	graph=parse()
	print('Parse done')

	airlines=getairlines(graph)
	finalRDF+=airlines
	airlines_data=genairlinedata(airlines)
  
	airport=getairports(graph)
	finalRDF+=airport	

	route=getroutes(graph)
	finalRDF+=route

	routes_data=getroutesdata(route,airport,airlines_data)

	#for f in finalRDF:
	#	print(f)
main()
