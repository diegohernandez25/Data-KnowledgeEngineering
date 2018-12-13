import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import sys 

def printMenu():
	print("1. Cities of a Country")
	print("2. Monuments of a City")
	print("0. Exit")
def queryCities(country):
	return"""
		SELECT 
			?label ?coords
		WHERE {
			?country rdfs:label """+"\""+str(country)+"\""+"""@en.
			?city wdt:P17 ?country.
			{
				?city wdt:P31 wd:Q1549591.
			}
			UNION
			{
				?city wdt:P31 wd:Q515.
			}
			OPTIONAL
			{
				?city wdt:P625 ?coords
			}
			?city rdfs:label ?label.
			FILTER(lang(?label) = "en")
		 }
	"""

def queryIsCity(city):
	return """
		ASK{
			?city rdfs:label """+"\""+str(city)+"\""+"""@en.
			{
				?city wdt:P31 wd:Q515.
			}
			UNION
			{
				?city wdt:P31 wd:Q1549591.
			}
		}	
	"""

def queryMonumentCities(city):
	return """
		SELECT
		  ?label ?coords
		{
		  ?city rdfs:label """+"\""+str(city)+"\""+"""@en.
		  ?city wdt:P31 wd:Q515.
		  ?city wdt:P1830 ?monuments.
		  ?monuments rdfs:label ?label.
		  OPTIONAL
		  {
			?monuments wdt:P625 ?coords
		  }
		  FILTER(lang(?label) = "en")
		} 	
	"""

def main():
	
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	while 1:
		keys = list()
		printMenu()
		opt = input(">>")
		if opt == str(1):
			keys.append("label")
			keys.append("coords")
			query = queryCities(input("Name of country >> "))
			print(str(query))
		
		elif opt == str(2):
			keys.append("label")
			keys.append("coords")
			city = input("Name of city >>")
			if not queryIsCity(city):
				print("City does not exist")
				continue
			query = queryMonumentCities(city)
			print(query)

		elif opt == str(0):
			print("Watchyouprofanity")
			sys.exit(1)
		else:
			print("Wrong Option")
			continue
		try:
			sparql.setQuery(query)
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()
		except:
			print("Error on query")
			continue
		for result in results["results"]["bindings"]:
			for k in keys:
				if result.get(k) : print(result[k]["value"])


main()
