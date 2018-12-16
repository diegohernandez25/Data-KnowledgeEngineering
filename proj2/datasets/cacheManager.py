from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from datetime import datetime
import json
import sys


class cacheManager:
	def __init__(self):
		self.endpoint = "http://localhost:7201"
		self.repo_name = "airlinesdotCache"
		self.client = ApiClient(endpoint = self.endpoint)
		self.accessor = GraphDBApi(self.client)
		self.count=0
		self.countroute=0

	def addtocache(self,source,destination,cost,dayofarrival,dayofdeparture,timeofarrival,timeofdeparture,distance,path):
		#TODO check if it already exist first
		_partof = "<http://www.airlinesdot.com/resources/pseudoroutes/flight_"+str(self.count)+">"
		print(_partof)
		query = """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>	
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		INSERT DATA{
			"""+_partof+""" psr:validuntil """+str(datetime.now().month)+""";
			ns2:sourceId <"""+source+""">;
			ns2:destinationId <"""+destination+""">;
			ns2:cost """+str(cost)+""";
			ns2:dayofarrival """+"\""+dayofarrival+"\""+""";
			ns2:dayofdeparture """+"\""+dayofdeparture+"\""+""";
			ns2:timeofarrival """+"\""+timeofarrival+"\""+"""^^xsd:time;
			ns2:timeofdeparture """+"\""+timeofdeparture+"\""+"""^^xsd:time;
			ns2:distance """+str(distance)+""";\n	
		"""
		
		if len(path) > 0:
			query+="psr:next psr:route_"+str(self.countroute)+".}"
		else:
			print("Flight does not have a route")
			sys.exit(1)
		path.pop(0) #First Flight
		print(query)
		self.countroute+=1
		input(">>ENTER")

		res=self.submitUpdate(query)
		
		while path:
			_r=path.pop(0)
			if path:
				_next ="psr:route_"+str(self.countroute+1)
				self.addPseudoRoute(_partof,self.countroute,_r,_next)
			else:
				self.addPseudoRoute(_partof, self.countroute,_r,)
			self.countroute+=1

	def addPseudoRoute(self,_partof, _id, _route,_next="\"None\""):
		query = """
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
			PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
			PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
			INSERT DATA{
				psr:route_"""+str(_id)+""" psr:routeid """+str(_id)+""";
				psr:route <"""+_route+""">;
				psr:next """+_next+""";
				psr:partof """+_partof+""".
			}
		"""
		print("[ addPseudoRoute  ] query: ",query)
		input(">>ENTER")
		res=self.submitUpdate(query)
		print("[ addPseudoRoute  ] res: ",res)

	def verifycache(self,source,destination):
		pass

	def submitQuery(self,query):
		payload_query = {"query":query}
		res= self.accessor.sparql_select(body=payload_query, repo_name= self.repo_name)
		return res

	def submitUpdate(self,query):
		payload_query = {"query":query}
		res = self.accessor.sparql_update(body=payload_query, repo_name=self.repo_name)
		return res

if __name__ == "__main__":
	cm = cacheManager()
	path=['http://openflights.org/resource/route/id/DDD','http://openflights.org/resource/route/id/EEE','http://openflights.org/resource/route/id/FFF','http://openflights.org/resource/route/id/GGG']
	cm.addtocache('http://openflights.org/resource/airport/id/BBB','http://openflights.org/resource/airport/id/CCC',155,'Saturday','Saturday',"09:50:00","23:01:00",655,path)
	cm.verifycache("http://openflights.org/resource/airport/id/BBB","http://openflights.org/resource/airport/id/CCC")
	

