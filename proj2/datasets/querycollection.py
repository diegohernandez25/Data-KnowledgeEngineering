def getRoutesAirport(uri):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX of: <http://openflights.org/resource/> 
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

		PREFIX ns1: <http://openflights.org/resource/route/>
		PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
		PREFIX ns3: <http://openflights.org/resource/airport/> 
		PREFIX ns4: <http://openflights.org/resource/airline/> 
		
		SELECT ?airportend ?dist ?price ?airlat ?airlon ?route
		WHERE{
			<"""+str(uri)+"""> a of:Airport.
			?route ns1:sourceId <"""+str(uri)+""">.
			?route ns1:destinationId ?airportend.
			?route ns2:cost ?price.
			?route ns2:distance ?dist.

			?airportend ns3:latitude ?airlat.
			?airportend ns3:longitude ?airlon.
		}
	"""


def getAirportCoords(uri):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
	PREFIX of: <http://openflights.org/resource/> 
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	
	SELECT ?airlat ?airlon
	WHERE{
		<"""+uri+"""> ns3:latitude ?airlat;
					  ns3:longitude ?airlon.
	}
	"""


def getAirportCity(city):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	
	SELECT ?airport ?airlat ?airlon
	WHERE{
		?airport ns3:city """+"\""+str(city)+"\""+""".
		?airport a of:Airport.
		?airport ns3:latitude ?airlat.
		?airport ns3:longitude ?airlon.
	}
	"""

def getAirportURI(name):
	return"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	
	SELECT ?airport ?airlat ?airlon
	WHERE{
		?airport rdfs:label """+"\""+str(name)+"\""+""".
		?airport a of:Airport.
		?airport ns3:latitude ?airlat.
		?airport ns3:longitude ?airlon.
	}
	"""
def getAirportCoord(uri):
	return """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX of: <http://openflights.org/resource/> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/> 
	PREFIX ns3: <http://openflights.org/resource/airport/> 
	PREFIX ns4: <http://openflights.org/resource/airline/> 
	SELECT ?lon ?lat
	WHERE{
		<"""+str(uri)+"""> a of:Airport.
		<"""+str(uri)+"""> ns3:latitude ?lat.
		<"""+str(uri)+"""> ns3:longitude ?lon.
	}
	"""
