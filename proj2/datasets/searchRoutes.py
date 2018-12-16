from search import *
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random
import math
from converter import *
import sys
import time


class AirportRoutes(SearchDomain):
	def __init__(self,endpoint,repo_name,client,accessor):
		self.endpoint = endpoint
		self.repo_name = repo_name
		self.client = client
		self.accessor = accessor

	def actions(self,node):
		actlist = []
		#print("Inside Actions Method:",repr(node))
		query = getRoutesAirport(node[0]) #TODO: check that node is an URI
		#print(query)
		res = queryGraphDB(query,self.accessor,self.repo_name)
		for e in res['results']['bindings']:
			dist =0
			actlist.append((node,e['airportend']['value'],e['dist']['value'],(e['airlat']['value'],e['airlon']['value']),e['route']['value'])) #TODO dist
			#actlist.append((node,e['airportend']['value'],e['cost']['value'],(e['airlat']['value'],e['airlon']['value']))) #TODO cost
		#print("actlist: ",repr(actlist))
		print('AAAAAAAAAAAAAAAAAAAAA',len(actlist))
		return actlist

	#Do I need this?? Ans: Probably not
	def result(self, node, action):
		(n1,n2,cost) = action
		if n1 == node:
			return n2

	def heuristic(self,node,destnode):
		#return 0
		src=(float(node[1][0]),float(node[1][1]))
		dest=(float(destnode[1][0]),float(destnode[1][1]))
		return distancecoord(src,dest)
		#return 10+10*distancecoord(src,dest)



		#OLD CODE
		query = getAirportCoord(node) #TODO: check that node is an URI
		res = queryGraphDB(query,self.accessor,self.repo_name)
		if(not len(res['results']['bindings'])==1):
			print("More than one coordinate")#TODO Handle the situation
			sys.exit(1)
		lat1=float(res['results']['bindings'][0]['lat']['value'])
		lon1=float(res['results']['bindings'][0]['lon']['value'])

		query = getAirportCoord(destnode)
		res = queryGraphDB(query,self.accessor,self.repo_name)
		if(not len(res['results']['bindings'])==1):
			print("More than one coordinate")#TODO Handle the situation
			sys.exit(1)
		lat2=float(res['results']['bindings'][0]['lat']['value'])
		lon2=float(res['results']['bindings'][0]['lon']['value'])

		heu = distancecoord((lat1,lon1),(lat2, lon2))
		#print("Heuristic: ",heu)
		return heu

def getAirportCity(city):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	
	SELECT ?airport ?airlat ?airlon
	WHERE{
		?airport ns3:city """+"\""+str(city)+"\""+""".
		?airport a of:Airport.
		?airport ns3:latitude ?airlat.
		?airport ns3:longitude ?airlon.
	}
	"""

def getAirportURI(name):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	
	SELECT ?airport ?airlat ?airlon
	WHERE{
		?airport rdfs:label """+"\""+str(name)+"\""+""".
		?airport a of:Airport.
		?airport ns3:latitude ?airlat.
		?airport ns3:longitude ?airlon.
	}
	"""
def getAirportCoord(uri):
	print('NOOOOOOOOO')
	return """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	SELECT ?lon ?lat
	WHERE{
		<"""+str(uri)+"""> a of:Airport.
		<"""+str(uri)+"""> ns3:latitude ?lat.
		<"""+str(uri)+"""> ns3:longitude ?lon.
	}
	"""

def getRoutesAirport(uri):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX of: <http://openflights.org/resource/> 
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

		PREFIX ns1: <http://openflights.org/resource/route/>
		PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
		PREFIX ns3: <http://openflights.org/resource/airport/> 
		PREFIX ns4: <http://openflights.org/resource/airline/> 
		
		SELECT ?airportend ?dist ?cost ?airlat ?airlon ?route
		WHERE{
			<"""+str(uri)+"""> a of:Airport.
			?route ns1:sourceId <"""+str(uri)+""">.
			?route ns1:destinationId ?airportend.
			?route ns2:cost ?cost.
			?route ns2:distance ?dist.

			?airportend ns3:latitude ?airlat.
			?airportend ns3:longitude ?airlon.
		}
	"""
def connectGraphDB():
	#endpoint = "http://localhost:7201"
	endpoint = "http://localhost:7200"
	repo_name = "airlinesdot"
	client = ApiClient(endpoint = endpoint)
	accessor = GraphDBApi(client)
	return endpoint,repo_name,client,accessor

def routemain():
	endpoint,repo_name,client,accessor = connectGraphDB()	
	query = getAirportURI("Dallas Fort Worth Intl")
	#print(query)
	res= queryGraphDB(query,accessor,repo_name)
	for e in res['results']['bindings']:
		print("---Airport---")
		print(e['airport']['value'])
		_uri = e['airport']['value']
		query = getAirportCoord(_uri)
		#print(query)
		res2=queryGraphDB(query,accessor,repo_name)
		for e2 in res2['results']['bindings']:
			print("---Coords---")
			print(e2['lon']['value'])
			print(e2['lat']['value'])
		
		query = getRoutesAirport(_uri)
		print(query)
		res2=queryGraphDB(query,accessor,repo_name)
		print("---ChildNodes---")
		for e2 in res2['results']['bindings']:
			print(e2['airportend']['value'])
		print()

def queryGraphDB(query,accessor,repo_name):
	payload_query = {"query":query}
	res = accessor.sparql_select(body = payload_query, repo_name = repo_name)
	return json.loads(res)

def search_path():
	endpoint,repo_name,client,accessor = connectGraphDB()	
	
	_orig= input("orig>>")
	#query= getAirportURI(_orig)
	query= getAirportCity(_orig)
	res= queryGraphDB(query,accessor,repo_name)
	print(query)
	if(len(res['results']['bindings'])!=1):
		#TODO: manage
		print("Zero or more than one Airport named after. Handle this later") #TODO
	_orig = (res['results']['bindings'][0]['airport']['value'],(res['results']['bindings'][0]['airlat']['value'],res['results']['bindings'][0]['airlon']['value']),None)
	print("Source Airport Node: ",_orig)
	_dest= input("dest>>")
	#query= getAirportURI(_dest)
	query= getAirportCity(_dest)
	print(query)
	res= queryGraphDB(query,accessor,repo_name)
	if(len(res['results']['bindings'])!=1):
		#TODO: manage
		print("Zero or more than one Airport named after. Handle this later") #TODO
	_dest = (res['results']['bindings'][0]['airport']['value'],(res['results']['bindings'][0]['airlat']['value'],res['results']['bindings'][0]['airlon']['value']),None) 
	print("Destiny Airport Node: ",_dest)
	
	route=AirportRoutes(endpoint,repo_name,client,accessor) 
	
	_limit = int(input("Max. number of flights>> "))
	my_prob = SearchProblem(route,_orig,_dest)
	#my_tree = SearchTree(my_prob,strategy="greedy",limit=_limit)
	#my_tree.strategy = "greedy"
	my_tree = SearchTree(my_prob,strategy="a_star",limit=_limit)
	my_tree.strategy = "a_star"
	#time.sleep(2) #TODO remove me
	repr(my_tree.search())
	sys.exit(1)

#routemain()
search_path()
