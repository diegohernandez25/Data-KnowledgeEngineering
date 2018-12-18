import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import sys 

def printMenu():
	print("1. Cities of a Country")
	print("2. Monuments of a City")
	print("3. Is a country")
	print("4. Is a city")
	print("5. Airport of a country")
	print("6. Country of a Continent")
	print("7. Cities with airport")
	print("0. Exit")


def queryCountryAirports(country):
	return"""
		SELECT 
			?label ?coords ?airport ?citylabel
		WHERE{
			?country rdfs:label """+"\""+str(country)+"\""+"""@en.
			?airport wdt:P31 wd:Q644371.
			?airport wdt:P17 ?country.
			?airport rdfs:label ?label.
			?airport wdt:P131 ?city.
			?city rdfs:label ?citylabel.
			OPTIONAL
			{
				?airport wdt:P625 ?coords
			}
			FILTER(lang(?label) = "en")
			FILTER(lang(?citylabel) = "en")
		}
	"""

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
def queryIsCountry(country):
	return"""
		ASK{
		  ?country rdfs:label """+"\""+str(country)+"\""+"""@en.
		  {
			?country wdt:P31 wd:Q3624078.
		  }
		  UNION{
			?country wdt:P31 wd:Q6256.
		  }
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

def queryCoord( _object):
	return"""
	SELECT ?coord
	WHERE{
		?object rdfs:label """+str(_object)+"""@en.
		?object wdt:P625 ?coord.
	}
	"""



def queryMonumentCities(city, limit =50):
	return """
	SELECT DISTINCT
?label ?coords ?monuments ?typelabel
WHERE{
  ?city rdfs:label """+"\""+str(city)+"\""+"""@en.
  {
    ?monuments wdt:P131 ?city.
  }
  UNION{
    ?city wdt:P1830 ?monuments.
  }
  ?monuments wdt:P31 ?type.
  ?type rdfs:label ?typelabel.
  ?monuments rdfs:label ?label.
  ?monuments wdt:P625 ?coords

  FILTER(lang(?label) = "en")
  FILTER(lang(?typelabel) = "en")
  FILTER(str(?typelabel)="museum" || str(?typelabel)="park" || str(?typelabel)="theater" || str(?typelabel)="church building"
  || str(?typelabel)="university" || str(?typelabel)="fort" || str(?typelabel)="sculpture" || str(?typelabel)="architectural structure"
  || str(?typelabel)="cathedral" || str(?typelabel)="stadium" || str(?typelabel)="cultural property" || str(?typelabel)="tourist destination")
}limit """+str(limit)+"""
	"""
#Paises dum continente
def countriesOfContinent(continent):
	return """
	SELECT
		?country ?label ?capitallabel ?coords
	WHERE{
		?continent rdfs:label """+"\""+str(continent)+"\""+"""@en.
		?continent wdt:P31 wd:Q5107.
		?country p:P30 [ps:P30 ?continent;].
		?country p:P31 [ps:P31 wd:Q6256;].
		?country rdfs:label ?label.
		?country wdt:P36 ?capital.
		?capital rdfs:label ?capitallabel.
		?capital wdt:P625 ?coords.
		FILTER(lang(?label) = "en")
		FILTER(lang(?capitallabel) = "en")
		SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }}
	
	"""
#cidades dum pais com aeroporto
def citysWithAirport(country):
	return """
	SELECT
		?label ?coord ?citylabel
	WHERE{
		?country rdfs:label """+"\""+str(country)+"\""+"""@en.
		?country p:P31 [ps:P31 wd:Q6256;].
		?airport wdt:P31 wd:Q644371.
		?airport wdt:P17 ?country.
		?airport rdfs:label ?label.
		?airport wdt:P625 ?coord.
		?airport wdt:P131 ?city.
		?city rdfs:label ?citylabel.
		FILTER(lang(?label) = "en")
		FILTER(lang(?citylabel) = "en")
		SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
	}
"""

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
def queryData(query, ask=False):
	try:
		print(query)
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		print("RESULTS:",str(results))
	except:
		print("Error on query")
		return -1
	if ask:
		return results['boolean']
	print(results["results"]["bindings"])
	return results["results"]["bindings"]

if __name__=="__main__":
	
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	while 1:
		ask = False
		ask_res = None
		keys = list()
		printMenu()
		opt = input(">>")
		if opt == str(1):
			keys.append("label")
			keys.append("coords")
			query = queryCities(input("Name of country >> "))
		
		elif opt == str(2):
			keys.append("label")
			keys.append("coords")
			keys.append("typelabel")
			city = input("Name of city >>")
			if not queryIsCity(city):
				print("City does not exist")
				continue
			query = queryMonumentCities(city)
	
		elif opt == str(3):
			ask = True
			query = queryIsCountry(input("Name of country>>"))

		elif opt == str(4):
			ask = True
			query = queryIsCity(input("Name of city>>"))

		elif opt == str(5):
			keys.append("label")
			keys.append("coords")
			keys.append("airport")
			keys.append("citylabel")
			query = queryCountryAirports(input("Name of country>>"))

		elif opt == str(6):
			keys.append("label")
			keys.append("coords")
			keys.append("capitallabel")
			query=countriesOfContinent(input("Name of Continent>>"))
		elif opt == str(7):
			keys.append("label")	
			keys.append("coord")	
			keys.append("citylabel")
			query=citysWithAirport(input("Name of Country>>"))

		elif opt == str(0):
			print("Watchyouprofanity")
			sys.exit(1)
		else:
			print("Wrong Option")
			continue
		try:
			print(query)
			sparql.setQuery(query)
			sparql.setReturnFormat(JSON)
			results = sparql.query().convert()
		except:
			print("Error on query")
			continue
		if ask:
			print(results)
			continue
		for result in results["results"]["bindings"]:
			for k in keys:
				if result.get(k) : print(result[k]["value"])
				#if result.get("coords") : 
					#_tuple=eval(result["coords"]["value"].replace("Point","").replace(" ",","))
					#print(_tuple[0])	

