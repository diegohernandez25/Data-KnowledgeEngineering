#TODO: custo = 10+Kilometer/10
from functools import reduce

class SearchDomain:
	# construtor
	def __init__(self):
		abstract
	# lista de accoes possiveis num estado
	def actions(self, state):
		abstract
	# resultado de uma accao num estado, ou seja, o estado seguinte
	def result(self, state, action):
		abstract
	# custo de uma accao num estado
	def cost(self, state, action):
		abstract
	# custo estimado de chegar de um estado a outro
	def heuristic(self, state, goal_state):
		abstract

class SearchProblem:
	#def __init__(self, domain, initial, goal):
	def __init__(self,domain,initial, goal):
		self.domain = domain
		self.initial = initial
		self.goal = goal
	def goal_test(self, state):
		return state == self.goal

class SearchNode:
	def __init__(self,state,parent, cost=0, prof=0, heur=0):
		self.state = state
		self.parent = parent
		self.cost=cost
		self.prof=prof
		self.heur=heur
	def get_parents(self):
		if(self.parent==None):
			return []
		return [self.parent.state]+self.parent.get_parents()

class SearchTree:

	# construtor
	def __init__(self,problem, strategy='a_star',limit=10):
		self.problem = problem
		root = SearchNode(problem.initial, None,0)
		print("this is route: ",str(root.state))
		self.open_nodes = [root]
		self.strategy = strategy
		self.prof=0
		self.limit=limit
		print("Limit:",self.limit)
		self.term=1
		self.non_term=0
		self.ration=0


	# obter o caminho (sequencia de estados) da raiz ate um no
	def get_path(self,node):
		if node.parent == None:
			return [node.state]
		path = self.get_path(node.parent)
		path += [node.state]
		return(path)

	# procurar a solucao
	def search(self):
		visited_nodes=[]
		while self.open_nodes != []:
			node=self.open_nodes.pop(0)
			print("Node: ",node.state)
			print("len(visited_nodes)=",len(visited_nodes))
			print("len(open_nodes)=",len(self.open_nodes))
			print("intersection=",list(set(visited_nodes) & set(map(lambda x: (x.state),self.open_nodes))))
			#print(self.open_nodes)
			#print(visited_nodes)
			input()
			if self.problem.goal[0]==node.state[0]:
				self.solution=node
				print(self.get_path(node))
				return self.get_path(node)
			visited_nodes.append(node.state)
			lnewnodes = []

			if node.prof==self.limit:
				continue
				
			for a in self.problem.domain.actions(node.state):
				newstate = (a[1],a[3],a[4])
				#print(newstate)
				newstatecost = node.cost+int(a[2]) 
				if reduce(lambda x,y: x and (y[0]!=newstate[0]),visited_nodes,True):
					lnewnodes += [SearchNode(newstate,node,newstatecost,node.prof+1,self.problem.domain.heuristic(node.state,self.problem.goal))]
				#else:
				#	print('NO')

			final=list()
			for new in lnewnodes:
				dup=list(filter(lambda x:x.state[0]==new.state[0],final))
				if len(dup)>1:
					print('YEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEET')
				if len(dup)!=0:
					if dup[0].cost>new.cost:
						final.remove(dup[0])
						final.append(new)
				else:
					final.append(new)

			self.add_to_open(final)

		self.solution=None
		return None


	# juntar novos nos a lista de nos abertos de acordo com a estrategia
	def add_to_open(self,lnewnodes):
		if self.strategy=='a_star':
			self.open_nodes[0:0]=lnewnodes
			#self.open_nodes=list(set(self.open_nodes))##Just to make sure there are no double choices
			self.open_nodes.sort(key=lambda node:node.heur+node.cost)
		elif self.strategy=='greedy':
			self.open_nodes.extend(lnewnodes)
			self.open_nodes.sort(key=lambda node: node.heur)
		else:
			print("strategy not implemented")
