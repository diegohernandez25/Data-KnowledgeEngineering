from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from datetime import datetime,timedelta
import json
import sys


class cacheManager:
	def __init__(self):
		self.endpoint = "http://localhost:7200"
		self.repo_name = "airlinesdotCache"
		self.client = ApiClient(endpoint = self.endpoint)
		self.accessor = GraphDBApi(self.client)

	def get_next_pflight(self):
		query="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>

		select ?o where { 
			?s a  psr:PseudoFlight.
			?s psr:flightid ?o
		} 
		order by desc(?o)
			limit 1
		"""
		lst=self.submitQuery(query)
		if len(lst)==0:
			sub=0
		else:
			sub=int(lst[0]['o'].split('/')[-1])+1

		ins="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		insert data{
			psr:flight_"""+str(sub)+""" a psr:PseudoFlight.
			psr:flight_"""+str(sub)+""" psr:flightid """+str(sub)+""".
		}
		"""
		self.submitUpdate(ins)
		return sub

	def get_next_proute(self):
		query="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>

		select ?o where { 
			?s a  psr:PseudoRoute.
			?s psr:routeid ?o.
		} 
		order by desc(?o)
			limit 1
		"""
		lst=self.submitQuery(query)
		if len(lst)==0:
			sub=0
		else:
			sub=int(lst[0]['o'].split('/')[-1])+1

		ins="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		insert data{
			psr:route_"""+str(sub)+""" a psr:PseudoRoute.
			psr:route_"""+str(sub)+""" psr:routeid """+str(sub)+""".
		}
		"""
		self.submitUpdate(ins)
		return sub

	def cleancache(self):
		query="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

		delete{
			?s ?a ?b.
			?rs ?rp ?ro.
		}
		where{
			?s psr:validuntil ?o.
			filter(?o<"""+'"'+str(datetime.now().date())+""""^^xsd:date).
			?s ?a ?b.
			?rs psr:partof ?s.
			?rs ?rp ?ro.
		}
		"""
		self.submitUpdate(query)
		

	def retrivefromcache(self,srcURI,dstURI):
		self.cleancache()
		ret=dict()
		for opt in ['price','distance','hop','time','flighttime']:
			ret[opt]=dict()
			ret[opt]['uri']=self.verifycache(srcURI,dstURI,opt)
			if ret[opt]['uri']==None:
				return None

		for opt in ret:
			pflightq="""
				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
				PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
				select ?cost ?price ?distance ?nrhops ?elapsedtime ?next
				where{

					?s	a psr:PseudoFlight;
						ns2:sourceId <"""+srcURI+""">;
						ns2:destinationId <"""+dstURI+""">;
						psr:optimize """+'"'+opt+"""\";
						psr:cost ?cost;
						psr:price ?price;
						psr:distance ?distance;
						psr:nrhops ?nrhops;
						psr:elapsedtime ?elapsedtime;
						psr:next ?next.
				}
			"""
			q=self.submitQuery(pflightq)[0]	
			rt=ret[opt]
			rt['cost']=q['cost']
			rt['price']=q['price']
			rt['distance']=q['distance']
			rt['nrhops']=q['nrhops']
			rt['elapsedtime']=q['elapsedtime']
			rt['route']=list()

			nextr=q['next']
			while True:
				prouteq="""
					PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
					PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
					PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
					select ?next ?route
					where{
						<"""+nextr+""">	psr:route ?route.
						optional{ <"""+nextr+"""> psr:next ?next.}
					}
				"""
				qr=self.submitQuery(prouteq)[0]
				rt['route'].append(qr['route'])
				if 'next' not in qr:
					break 
				nextr=qr['next']
						
		return ret	


	def addtocache(self,route):
		if len(route['route'])==0:
			print('Empty path')
			return

		flightid=self.get_next_pflight()

		if self.verifycache(route['srcURI'],route['dstURI'],route['optimize']):
			return None

		_partof = "http://www.airlinesdot.com/resources/pseudoroutes/flight_"+str(flightid)
		#route valid for one month
		prouteid=self.get_next_proute()
		query = """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>	
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		INSERT DATA{
			<"""+_partof+"""> psr:validuntil """+'"'+str((datetime.now()+timedelta(weeks=4)).date())+"""\"^^xsd:date;
			a psr:PseudoFlight;
			ns2:sourceId <"""+route['srcURI']+""">;
			ns2:destinationId <"""+route['dstURI']+""">;
			psr:optimize """+'"'+str(route['optimize'])+"""";
			psr:cost """+str(route['cost'])+""";
			psr:price """+str(route['price'])+""";
			psr:distance """+str(route['distance'])+""";
			psr:nrhops """+str(route['nrhops'])+""";
			psr:elapsedtime """+str(route['elapsedtime'])+""";

			psr:next psr:route_"""+str(prouteid)+""".
		}"""
		
		res=self.submitUpdate(query)
		
		path=route['route'][:]
		while path:
			_r=path.pop(0)
			if path:
				nextid=self.get_next_proute()
				_next ="psr:route_"+str(nextid)
				self.addPseudoRoute('<'+_partof+'>',prouteid,_r,_next)
				prouteid=nextid
			else:
				self.addPseudoRoute('<'+_partof+'>', prouteid,_r,)
	
		return _partof 

	def addPseudoRoute(self,_partof, _id, _route,_next=None):
		query = """
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
			PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
			PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
			INSERT DATA{
				psr:route_"""+str(_id)+""" psr:routeid """+str(_id)+""";
				a psr:PseudoRoute;
				psr:route <"""+_route+""">;"""+ (("""
				psr:next """+_next+""";""") if _next!=None else "") +""" 
				psr:partof """+_partof+""".
			}
		"""
		res=self.submitUpdate(query)

	def verifycache(self,source,destination,optimize):
		query="""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX psr: <http://www.airlinesdot.com/resources/pseudoroutes/>
		PREFIX ns2: <http://www.airlinesdot.com/resource/route/>

		select ?s where { 
			?s ns2:sourceId <"""+source+""">.
			?s ns2:destinationId <"""+destination+""">.
			?s psr:optimize """+'"'+optimize+"""\".
		} 
		"""
		lst=self.submitQuery(query)
		if len(lst)==0:
			return None
		else:
			return lst[0]['s']
		

	def submitQuery(self,query):
		payload_query = {"query":query}
		res = self.accessor.sparql_select(body = payload_query, repo_name = self.repo_name)
		results=json.loads(res)['results']['bindings']
		ret=list()
		for r in results:
			tmp=dict()
			for k in r:
				tmp[k]=r[k]['value']
			ret.append(tmp)
		return ret

	def submitUpdate(self,query):
		payload_query = {"update":query}
		res = self.accessor.sparql_update(body=payload_query, repo_name=self.repo_name)
		return res
