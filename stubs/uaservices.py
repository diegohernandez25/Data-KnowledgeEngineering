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
		#self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sac/senhas/?date=2018-10-17&count=100')

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
		return etree.XMLSchema(etree.parse('UAParkingSchema.xsd')).validate(self.xml)

	def _fillstruct(self):
		self.parking = dict()
		for park in self.xml.findall('./Estacionamento'):
			self.parking[park.find('./ID').text] = {'Nome': park.find('./Nome').text,\
				'Latitude': park.find('./Latitude').text,\
				'Longitude': park.find('./Longitude').text,\
				'Capacidade':park.find('./Capacidade').text,\
				'Ocupado': park.find('./Ocupado').text,\
				'Livre': park.find('./Livre').text}

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



a=SASService()
a.get()
print(a.lunch)


a=SACService()
a.get()
print(a.tickets)

a = UAParking()
a.get()
print(a.parking)
