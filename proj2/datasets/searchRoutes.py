from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import json
from functools import reduce


#TODO settings.py
#endpoint = "http://localhost:7201"

class routeFinder():

	def __init__(self,srcuri,dsturi,optimize):
		self.optimize=optimize
		self.repo_name, self.accessor = connectGraphDB()
		qsrc=queryGraphDB(getAirportCoords(srcuri),self.accessor, self.repo_name)
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
				#print('FOUND')
				#print(node)
				#print('Cost: ',node['cost'])
				#print('Price: ',routeFinder.sum_of_param(node,'price'))
				#print('Distance: ',routeFinder.sum_of_param(node,'distance'))
				#print('NrHops: ',node['hop'])
				return {'route':routeFinder.node_route(node),'cost':node['cost'],'price':routeFinder.sum_of_param(node,'price'),'distance':routeFinder.sum_of_param(node,'distance'),'nrhops':node['hop']}	
				continue

			for hop in next_hops:
				if reduce(lambda x,y: x and y['uri']!=hop['uri'],self.visited_nodes,True): #FIXME	

					dup=list(filter(lambda x: x['uri']==hop['uri'],self.open_nodes))
					if len(dup)>1:
						raise Exception('Shit')
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
				raise Exception('Shit')
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
			hops.append(h)
		return hops
			
	
		
	def cost(self,node,hop):
		if self.optimize=='price':
			return node['cost']+float(hop['price'])
		elif self.optimize=='distance':
			return node['cost']+float(hop['dist']) 
		elif self.optimize=='hop':
			return node['hop']+1
		else:
			raise Exception('Boom')
		
			
	def heuristic(self,node):
		return 0 #FIXME FIXME FIXME NON ADMISSIBLE HEURISTICS
		if self.optimize=='price':
			dist=distancecoord(self.dstcoord,node['coord'])
			return 10*dist/100+10
		elif self.optimize=='distance':
			return dist
		elif self.optimize=='hop':
			return 0 #uniform search
		else:
			raise Exception('Boom')
			
		
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

def main():
	#a=routeFinder('http://openflights.org/resource/airport/id/1638','http://openflights.org/resource/airport/id/1636','price')	
	print('PRICE')
	a=routeFinder('http://openflights.org/resource/airport/id/2279','http://openflights.org/resource/airport/id/2851','price')	
	print(a.get_route())

	print('DISTANCE')
	a=routeFinder('http://openflights.org/resource/airport/id/2279','http://openflights.org/resource/airport/id/2851','distance')	
	print(a.get_route())

	print('HOP')
	a=routeFinder('http://openflights.org/resource/airport/id/2279','http://openflights.org/resource/airport/id/2851','hop')	
	print(a.get_route())

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
