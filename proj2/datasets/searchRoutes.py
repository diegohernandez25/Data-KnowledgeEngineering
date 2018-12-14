#from search import *
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random
import math
from converter import *
'''
class AirportRoutes(SearchDomain):
	def __init__(self,connections):
		self.connections = connections

	def actions(self,node):
		actlist = []
		for (n1,n2,dist) in self.connections:
			if(n1 == node):
				actlist.append((n1,n2,dist))
			elif(n2 == node):
				actlist.append((n2,n1,dist))
		return actlist
	#Do I need this?? Ans: Probably not
	def cost(self, state, action):
		(n1,n2,dist) = action
		#(n1,n2) = action
		for (node1,node2,distance) in self.connections:
			if((node1==n1 and node2==n2) or (node1==n2 and node2==n1)):
				return distance

	def result(self, cidade, action):
		(n1,n2,dist) = action
		#(n1,n2) = action
		if cidade == n1:
			return n2
			#return n2.id

	def heuristic(self,state,goal_state):
		return distancecoord((state.lat,state.lon),(goal_state.lat, goal_state.lon))
'''
def getAirportURI(name):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX pair: <http://openflights.org/resource/airport/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	
	SELECT ?airport
	WHERE{
		?airport rdfs:label """+"\""+str(name)+"\""+""".
		?airport a of:Airport.
	}
	"""
def getAirportCoord(uri):
	return """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX pair: <http://openflights.org/resource/airport/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	SELECT ?lon ?lat
	WHERE{
		<"""+str(uri)+"""> a of:Airport.
		<"""+str(uri)+"""> pair:latitide ?lat.
		<"""+str(uri)+"""> pair:longtitude ?lon.
	}
	"""

def getRoutesAirport(uri):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX of: <http://openflights.org/resource/> 
		PREFIX pair: <http://openflights.org/resource/airport/> 
		PREFIX rout: <http://openflights.org/resource/route/>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

		SELECT ?airportend
		WHERE{
			<"""+str(uri)+"""> a of:Airport.
			?route rout:sourceId <"""+str(uri)+""">.
			?route rout:destinationId ?airportend.
		}
	"""

def routemain():
	endpoint = "http://localhost:7201"
	#endpoint = "http://localhost:7200"
	repo_name = "airlinesdot"
	client = ApiClient(endpoint = endpoint)
	accessor = GraphDBApi(client)
	

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
		res2=queryGraphDB(query,accessor,repo_name)
		print("---ChildNodes---")
		for e2 in res2['results']['bindings']:
			print(e2['airportend']['value'])
		print()

def queryGraphDB(query,accessor,repo_name):
	payload_query = {"query":query}
	res = accessor.sparql_select(body = payload_query, repo_name = repo_name)
	return json.loads(res)

routemain()
