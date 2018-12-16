from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

class cacheManager:
	def __init__():
		#self.endpoint = "http://localhost:7201"
		self.endpoint = "http://localhost:7200"
		self.repo_name = "airlinesdotCache"
		self.client = ApiClient(endpoint = endpoint)
		self.accessor = GraphDBApi(client)

	def addtocache(
