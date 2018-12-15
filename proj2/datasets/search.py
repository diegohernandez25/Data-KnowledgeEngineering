#TODO: custo = 10+Kilometer/10

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
	#def __str__(self):
		#pass
		#return "no(" + str(self.state) + "," + str(self.parent) + ","+str(self.cost)+","+str(self.prof)")"
	#def __repr__(self):
		#return str(self)
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
		print("Hey")
		while self.open_nodes != []:
			node = self.open_nodes.pop(0)
			print("Node: ",node.state)
			if self.problem.goal_test(node.state):
				print("Path",self.get_path(node))
				print("Found it")
				return self.get_path(node), node.cost, node.prof
			#Restrict Dept
			if(node.prof>=self.limit):
				print("Number of flights were exceeded.")
				continue
			lnewnodes = []
			for a in self.problem.domain.actions(node.state):
				#print("Analysing childs of node:",a[0])
				#print("Path: :",repr(self.get_path(node)))	
				#print("Cost: ",a[2])
				newstate = a[1]
				if newstate not in node.get_parents():
				    lnewnodes += [SearchNode(newstate,node,node.cost+int(a[2]),node.prof+1, self.problem.domain.heuristic(node.state,newstate))]
			#	else:
			#		print("Nodes remaining")
			self.add_to_open(lnewnodes)
		return None

	# juntar novos nos a lista de nos abertos de acordo com a estrategia
	def add_to_open(self,lnewnodes):
		if self.strategy=='a_star':
			self.open_nodes[0:0]=lnewnodes
			self.open_nodes.sort(key=lambda node:node.heur+node.cost)
			self.open_nodes=list(set(self.open_nodes))##Just to make sure there are no double choices
		else:
			print("strategy not implemented")
