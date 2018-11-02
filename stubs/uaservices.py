import urllib.request, json
import abc
from lxml import etree

#TODO CHECK XML SCHEMA AFTER EVERY API CHANGE
class XMLService(abc.ABC):
	@abc.abstractmethod
	def _validate(self):
		pass

	@abc.abstractmethod
	def _fetch(self):
		pass

	@abc.abstractmethod
	def _fillstruct(self):
		pass

	def get(self):
		self._fetch()
		if not self._validate():
			raise Exception('XML not compliant')
		self._fillstruct()

	def loadfileurl(url,decode=0):
		fl=urllib.request.urlopen(url)
		#return '\n'.join(map(lambda x:x.decode("utf-8"),list(fl)))
		#return fl.read()
		return fl.read().decode() if decode else fl.read()

	def loadxmlurl(url,decode=0):
		return etree.fromstring(XMLService.loadfileurl(url,decode))

class SASService(XMLService):
	def __init__(self):
		self.txml=None
		self.lunch=None
		self.dinner=None

	def _fetch(self):
		self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sas/ementas')

	def _validate(self):
		return etree.XMLSchema(etree.parse('SASServiceSchema.xsd')).validate(self.txml)

	def _fillstruct(self):
		self.lunch=dict()
		self.dinner=dict()
		for menu in self.txml.findall('.//menu'):
			if menu.attrib['disabled']!="0":
				continue

			entry=dict()
			for item in menu.findall('./items/item'):
				entry[item.attrib['name']]=item.text

			entry['weekday']=menu.attrib['weekday']
			if menu.attrib['meal']=='Almoço':
				self.lunch[menu.attrib['canteen']]=entry
			elif menu.attrib['meal']=='Jantar':
				self.dinner[menu.attrib['canteen']]=entry
			else:
				raise Exception('Unknown meal time')

class SACService(XMLService):
	def __init__(self):
		self.txml=None
		self.tickets=None

	def _fetch(self):
		self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sac/senhas')

	def _validate(self):
		return etree.XMLSchema(etree.parse('SACServiceSchema.xsd')).validate(self.txml)

	def _fillstruct(self):
		self.tickets=dict()
		if self.txml[0].attrib['count']=="0": #Closed
			return

		for ticket in self.txml.findall('./items/item'):
			letter=ticket.find('./letter').text
			if not letter in self.tickets:
				self.tickets[letter]={'name': ticket.find('./desc').text, \
										'latest': ticket.find('./latest').text, \
										'wait_line_size': ticket.find('./wc').text}

class UAParking(XMLService):
	def __init__(self):
		self.json = None
		self.xml = None
		self.parking = None

	def _fetch(self):
		self.json = json.loads(XMLService.loadfileurl("http://services.web.ua.pt/parques/parques",1))
		self.JSON2XML()

	def _validate(self):
		#return etree.XMLSchema(etree.parse('UAParkingSchema.xsd')).validate(self.xml)
		return True
	def _fillstruct(self):
		self.parking = dict()
		for park in self.xml.findall('./Estacionamento'):
			self.parking[park.find('./ID').text] = {'Nome': park.find('./Nome').text,\
				'Latitude': park.find('./Latitude').text,\
				'Longitude': park.find('./Longitude').text,\
				'Capacidade':park.find('./Capacidade').text,\
				'Ocupado': park.find('./Ocupado').text,\
				'Livre': park.find('./Livre').text,\
				'Color': self.color_status(int(park.find('./Ocupado').text),int(park.find('./Capacidade').text))}

	def JSON2XML(self):
		tmp = None
		root,endroot = self.create_element("Estacionamentos")
		tmp = self.create_element("Timestamp")
		self.xml=root+tmp[0]+str(self.get_timestamp())+tmp[1]

		for e in self.get_all_parkinglots():
			parent, endparent = self.create_element("Estacionamento")
			self.xml+=parent
			for k,v in e.items():
				child,endchild = self.create_element(k if isinstance(k,str) else str(k))
				self.xml+=child+str(v)+endchild
			self.xml+=endparent

		self.xml+=endroot
		self.xml = etree.fromstring(self.xml)

	def create_element(self,str):
		elem = "<"+str+">"
		return elem, elem[:1]+'/'+elem[1:]

	def get_timestamp(self):
		if not self.json: self._feth()
		return dict(self.json[0])["Timestamp"]

	def get_all_parkinglots(self):
		return list(map(lambda x: dict(x), self.json[1:]))

	def color_status(self, occupied, capacity):
		if occupied<0: occupied=0

		_per = occupied/capacity
		if _per>90:
			return "#F4BC8B"
		elif _per>75:
			return "#D87777"
		elif _per>50:
			return "#F4D386"
		else:
			return "#86BA7A"

class UANews(XMLService):
	def __init__(self):
		self.xml = None
		self.parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
		self.news = None

	def _fetch(self):
		self.xml = etree.fromstring(bytes(bytearray(XMLService.loadfileurl('https://uaonline.ua.pt/xml/contents_xml.asp?&lid=1&i=11',1), encoding='utf-8')))
		print(self.xml)

	def _validate(self):
		#TODO: Figure how to validate xml with schema
		#return etree.XMLSchema(etree.parse('UANews.xsd')).validate(self.xml)
		return True

	def _fillstruct(self):
		self.news = dict()
		count = 0
		flag = True
		for n in self.xml.findall('./channel/item'):
			self.news[count] = {	'guid': n.find('./guid').text,\
									'title': n.find('./title').text,\
									'image': self.get_image(n.find('./description').text),\
									'image_thumb': self.get_image(n.find('./description').text,True),\
									'description': self.get_description(n.find('./description').text),\
									'pubDate':n.find('./pubDate').text,\
									'flag':flag}

			flag = not flag
			count+=1
			#print(self.news)
			#print("Description: "+n.find('./description').text)

	def specific_fectch(self,dt = None,n = None, di = None, df = None, d=None, i =1,lid=11):
		url = 'https://uaonline.ua.pt/xml/contents_xml.asp?&lid=1&i=11'
		if(dt): url+='&dt='+str(dt)+'&'
		if(di): url+='&dt'+di+'&'
		if(df): url+='&dt'+df+'&'
		if(d): url+='&dt'+str(d)+'&'
		url+='&dt'+str(i)+'&lid'+str(lid)
		self.xml = etree.fromstring(bytes(bytearray(XMLService.loadfileurl(url))));
		#TODO: Validate
		"""if not self._validate()
			raise Exception('XML not compliant')
		"""
		self._fillstruct()

	def get_image(self, string, thumb = False):
		#TODO Image metadata has also valuable data that we may use if needed
		#print("image :"+string[string.find('https'):string.find('jpg')+ len('jpg')])
		return string[string.find('https'):string.find('jpg')+ len('jpg')] if thumb else\
		string[string.find('https'): string.find('_thumb')]+'.jpg'


	def get_description(self, string ):
		#print("Only Description: "+ string[string.find('>')+1:])
		return string[string.find('>')+1:]


class WeatherService(XMLService):
    def __init__(self):
        self.txml=None
        #self.lastupdate=None
        self.weather=None

    def _fetch(self):
        self.txml=XMLService.loadxmlurl('https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/2742611')

    def _validate(self):
        return True

    def _fillstruct(self):
        self.weather=[]

        for item in self.txml.findall('.//item'):
            entry = dict()
            title = item.find('title').text.split(":")
            entry["Weekday"] = title[0]
            entry["Status"]= title[1].split(",")[0][1:]

            description = item.find('description').text.split(",")
            for field in description:
                field = field.split(":")
                tmp = field[0].split(" ")
                if tmp[-1]=="Temperature":
                    entry[tmp[-2] + " " + tmp[-1]] = field[1].split(" ")[1]
                else:
                    entry[field[0][1:]] = field[1][1:]

            self.weather.append(entry)


# a=SASService()
# a.get()
# print(a.lunch)
#
#
# a=SACService()
# a.get()
# print(a.tickets)
# a = UAParking()
# a.get()
# print(a.parking)
#
#a = UANews()
#a.get()
#print(a.news)
