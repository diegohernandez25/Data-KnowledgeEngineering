from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import json
from functools import reduce
from datetime import datetime,timedelta,date
from cacheManager import cacheManager

class routeFinder():

	def __init__(self):
		self.repo_name, self.accessor = connectGraphDB()

	def configure(self,srcuri,dsturi,optimize):
		self.optimize=optimize
		qsrc=queryGraphDB(getAirportCoords(srcuri),self.accessor,self.repo_name)
		srccoord=(float(qsrc[0]['airlat']),float(qsrc[0]['airlon']))
		
		qdst=queryGraphDB(getAirportCoords(dsturi),self.accessor, self.repo_name)
		self.dstcoord=(float(qdst[0]['airlat']),float(qdst[0]['airlon']))
		self.dsturi=dsturi

		src=dict()
		src['uri']=srcuri
		src['coord']=srccoord
		src['route']=None
		src['parent']=None
		src['heuristic']=None
		src['cost']=0
		src['hop']=0
		src['price']=0
		src['distance']=0
		src['elapsedtime']=0
		src['duration']=0
		src['tod']=None

		self.open_nodes=list()
		self.visited_nodes=list()
		self.open_nodes.append(src)


	def get_route(self):

		while self.open_nodes!=[]:
			
			node=self.open_nodes.pop(0)	
			self.visited_nodes.append(node)	

			next_hops=self.possible_hops(node)	
			next_hops=self.handle_dups(next_hops)

			print('\r',len(self.visited_nodes),'\t',len(self.open_nodes),end='')


			if node['uri']==self.dsturi:
				return {'route':routeFinder.node_route(node),'cost':node['cost'],'price':routeFinder.sum_of_param(node,'price'),'distance':routeFinder.sum_of_param(node,'distance'),'nrhops':node['hop'],'elapsedtime':node['elapsedtime']}	

			for hop in next_hops:
				if reduce(lambda x,y: x and y['uri']!=hop['uri'],self.visited_nodes,True): 

					dup=list(filter(lambda x: x['uri']==hop['uri'],self.open_nodes))
					if len(dup)>1:
						raise Exception('There are more than one duplicate entry on the opennodes array')
					elif len(dup)==1:
						if dup[0]['cost']>hop['cost']:
							self.open_nodes.remove(dup[0])
							self.open_nodes.append(hop)
					else:	
						self.open_nodes.append(hop)
			
			self.sort_open_nodes()

	def node_route(node):
		return (routeFinder.node_route(node['parent'])+[node['route']]) if node['parent'] else list()

	def sum_of_param(node,key):
		return node[key]+(routeFinder.sum_of_param(node['parent'],key) if node['parent'] else 0)					
		
	def sort_open_nodes(self):
		self.open_nodes.sort(key=lambda node:node['heuristic']+node['cost'])


	def handle_dups(self,nodes):
		newlist=list()
		for node in nodes:
			dup=list(filter(lambda x: x['uri']==node['uri'],newlist))
			if len(dup)>1:
				raise Exception('There are more than one duplicate entry on the nodes array')
			elif len(dup)==1:
				if dup[0]['cost']>node['cost']:
					newlist.remove(dup[0])
					newlist.append(node)
				
			else:
				newlist.append(node)
		return newlist

	def possible_hops(self,node):
		hop_data=queryGraphDB(getRoutesAirport(node['uri']), self.accessor, self.repo_name)
		hops=list()
		for hd in hop_data:
			h=dict()
			h['uri']=hd['airportend']
			h['coord']=(float(hd['airlat']),float(hd['airlon']))
			h['route']=hd['route']
			h['parent']=node
			h['heuristic']=self.heuristic(node)
			h['cost']=self.cost(node,hd)
			h['hop']=node['hop']+1
			h['price']=float(hd['price'])
			h['distance']=float(hd['dist'])
			h['elapsedtime']=self.elapsedtime(node,hd) if self.optimize!='time' and self.optimize!='flighttime' else h['cost']
			h['duration']=routeFinder._dt_to_rel_sec(datetime.strptime(hd['duration'],'%H:%M:%S'))
			h['tod']=routeFinder._dt_to_rel_sec(datetime.strptime(hd['tod'],'%H:%M:%S'))
	
			#if h['elapsedtime']!=h['cost']:
			#	print(h['elapsedtime'],' ',h['cost'])
			#	import sys
			#	sys.exit(0)

			#print((h['duration']-datetime(1900,1,1)).total_seconds())
			#print(h['duration'].date()+timedelta(days=1))
			hops.append(h)
		return hops

	def _t_to_dt(t):
		return datetime.combine(datetime(1970,1,1),t)

	def _dt_to_sec(dt):
		return (dt-datetime(1970,1,1)).total_seconds()#-3600

	def _sec_to_dt(sec):
		return datetime.fromtimestamp(sec)

	def _dt_to_rel_sec(dt):
		t=dt.time()	
		dtt=routeFinder._t_to_dt(t)
		return routeFinder._dt_to_sec(dtt)

	def elapsedtime(self,node,hop):
		duration=routeFinder._dt_to_rel_sec(datetime.strptime(hop['duration'],'%H:%M:%S'))

		if node['tod']==None: #fist node			
			return duration

		tod=routeFinder._dt_to_rel_sec(datetime.strptime(hop['tod'],'%H:%M:%S'))
		rcost=routeFinder._dt_to_rel_sec(routeFinder._sec_to_dt(node['cost']))

		if rcost>tod:
			waiting_time=24*60*60-rcost+tod
		else:
			waiting_time=tod-rcost

		#return node['elapsedtime']+duration
		#return node['elapsedtime']+duration
		return node['elapsedtime']+duration+(waiting_time if self.optimize!='flighttime' else 0)

		
		
	def cost(self,node,hop):
		if self.optimize=='price':
			return node['cost']+float(hop['price'])
		elif self.optimize=='distance':
			return node['cost']+float(hop['dist']) 
		elif self.optimize=='hop':
			return node['hop']+1
		elif self.optimize=='time' or self.optimize=='flighttime':
			return self.elapsedtime(node,hop)
		else:
			raise Exception('Unsuported optimize parameter')
		
			
	def heuristic(self,node):
		return 0 #FIXME FIXME FIXME NON ADMISSIBLE HEURISTICS
		if self.optimize=='price':
			dist=distancecoord(self.dstcoord,node['coord'])
			return 10*dist/100+10
		elif self.optimize=='distance':
			return dist
		elif self.optimize=='hop':
			return 0 #uniform search
		elif self.optimize=='time' or self.optimize=='flighttime':
			return 0 #uniform search
		else:
			raise Exception('Unsuported optimize parameter')
			
def connectGraphDB():
	endpoint = "http://localhost:7200"
	repo_name = "airlinesdot"
	client = ApiClient(endpoint=endpoint)
	accessor = GraphDBApi(client)
	return repo_name, accessor

def queryGraphDB(query,accessor,repo_name):
    payload_query = {"query":query}
    res = accessor.sparql_select(body = payload_query, repo_name = repo_name)
    results=json.loads(res)['results']['bindings']
    ret=list()
    for r in results:
        tmp=dict()
        for k in r:
            tmp[k]=r[k]['value']
        ret.append(tmp)
    return ret
		
def routeFinderNAME(srcCity,dstCity):
	repo_name,accessor = connectGraphDB()	
	srcAirports=queryGraphDB(getAirportCity(srcCity),accessor,repo_name)	
	dstAirports=queryGraphDB(getAirportCity(dstCity),accessor,repo_name)	

	print('len(srcAirports)=',len(srcAirports))
	print('len(dstAirports)=',len(dstAirports))

	for src in srcAirports:
		for dst in dstAirports:
			#print(dst['airport'])
			route=routeFinderURI(src['airport'],dst['airport'])
			if route!=None:
				return route
	return None

def routeFinderURI(srcuri,dsturi,rf=routeFinder()):

	cache=cacheManager()
	ch=cache.retrivefromcache(srcuri,dsturi)
	if ch!=None:
		return ch

	ret=dict()
	for opt in ['price','distance','hop','time','flighttime']:
		print('AAA')
		rf.configure(srcuri,dsturi,opt)
		ret[opt]=rf.get_route()
		if ret[opt]==None:
			return None

	addroutestocache(ret,srcuri,dsturi)
	return ret

def addroutestocache(routes,srcURI,dstURI):
	cache=cacheManager()
	for route in routes:
		rt=dict(routes[route])
		rt['optimize']=route
		rt['srcURI']=srcURI
		rt['dstURI']=dstURI
		routes[route]['uri']=cache.addtocache(rt)
		
def main():
	#print(routeFinderURI('http://openflights.org/resource/airport/id/2279','http://openflights.org/resource/airport/id/2851'))
	#print(routeFinderNAME('Porto','New York'))
	#print(routeFinderNAME('Porto','Lisbon'))
	print(routeFinderNAME('Funchal','Caracas'))
	#print(routeFinderURI('http://openflights.org/resource/airport/id/1636','http://openflights.org/resource/airport/id/3797'))

	#print('TOTAL TIME')
	#a=routeFinder('http://openflights.org/resource/airport/id/2279','http://openflights.org/resource/airport/id/2851','time')  
	#print(a.get_route())

if __name__=='__main__':
	from querycollection import *
	from converter import distancecoord
	main()
else:
	from datasets.querycollection import *
	from datasets.converter import distancecoord
