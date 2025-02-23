def getRoutesAirport(uri):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX of: <http://openflights.org/resource/>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

		PREFIX ns1: <http://openflights.org/resource/route/>
		PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
		PREFIX ns3: <http://openflights.org/resource/airport/>
		PREFIX ns4: <http://openflights.org/resource/airline/>

		SELECT ?airportend ?dist ?price ?airlat ?airlon ?route ?duration ?toa ?tod
		WHERE{
			<"""+str(uri)+"""> a of:Airport.
			?route ns1:sourceId <"""+str(uri)+""">.
			?route ns1:destinationId ?airportend.
			?route ns2:cost ?price.
			?route ns2:distance ?dist.
			?route ns2:duration ?duration.
			?route ns2:timeofarrival ?toa.
			?route ns2:timeofdeparture ?tod.

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

	SELECT ?airport ?airlat ?airlon ?label ?iata ?country ?city
	WHERE{
		?airport ns3:city """+"\""+str(city)+"\""+""".
		?airport a of:Airport.
		?airport ns3:latitude ?airlat.
		?airport ns3:longitude ?airlon.
		?airport ns3:iata ?iata.
		?airport ns3:country  ?country.
		?airport ns3:city  ?city.
		?airport rdfs:label ?label.
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
def getInfoRoute(uri):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX of: <http://openflights.org/resource/>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

		PREFIX ns1: <http://openflights.org/resource/airport/>
		PREFIX ns2: <http://openflights.org/resource/route/>
		PREFIX ns3: <http://www.airlinesdot.com/resource/route/>
		PREFIX ns4: <http://openflights.org/resource/airline/>


		SELECT ?airline ?airlineIdLabel ?destination ?destinationId ?sourceId ?destinationIdLabel ?plane ?source ?sourceIdLabel ?cost ?distance ?duration ?timeofarrival ?timeofdeparture

		WHERE{
			<"""+uri+"""> ns2:airline ?airline ;

			 ns2:airlineId ?airlineId;
			 ns2:destination ?destination;
			 ns2:destinationId ?destinationId;
			 ns2:source ?source;
			 ns2:sourceId ?sourceId;
			 ns3:cost ?cost;
			 ns3:distance ?distance;
			 ns3:duration ?duration;
			 ns3:timeofarrival ?timeofarrival;
			 ns3:timeofdeparture ?timeofdeparture.

			 ?airlineId rdfs:label ?airlineIdLabel.
			 ?destinationId rdfs:label ?destinationIdLabel.
			 ?sourceId rdfs:label ?sourceIdLabel.
}
	"""
def getCitysWithAirports(country):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX of: <http://openflights.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        PREFIX ns1: <http://openflights.org/resource/airport/>
        PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
        PREFIX ns3: <http://openflights.org/resource/airport/>
        PREFIX ns4: <http://openflights.org/resource/airline/>
        SELECT ?citylabel
        WHERE{

            ?airport ns1:country """+"\""+str(country)+"\""+""".

            ?airport a of:Airport.
            ?airport ns1:city ?citylabel.
        }
		"""

def getAirportsFromCountry(country):
	return """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX of: <http://openflights.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        PREFIX ns1: <http://openflights.org/resource/airport/>
        PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
        PREFIX ns3: <http://openflights.org/resource/airport/>
        SELECT ?airport ?lat ?lon
        WHERE{

            ?airport ns1:country """+"\""+str(country)+"\""+""".

            ?airport a of:Airport.
			?airport ns1:latitude ?lat. 
			?airport ns1:longitude ?lon. 
        }
		"""

def getAirportInfo(uri):
	return """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX of: <http://openflights.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	PREFIX ns1: <http://openflights.org/resource/route/>
	PREFIX ns2: <http://www.airlinesdot.com/resource/route/>
	PREFIX ns3: <http://openflights.org/resource/airport/>
	PREFIX ns4: <http://openflights.org/resource/airline/>
	SELECT ?airlat ?airlon ?label ?iata ?country ?city
	WHERE{
		<"""+uri+"""> a of:Airport.
		<"""+uri+"""> ns3:latitude ?airlat.
		<"""+uri+"""> ns3:longitude ?airlon.
		<"""+uri+"""> ns3:iata ?iata.
		<"""+uri+"""> ns3:country  ?country.
		<"""+uri+"""> ns3:city  ?city.
		<"""+uri+"""> rdfs:label ?label.
	}
	"""