import urllib.request
import abc
from lxml import etree


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

	def loadfileurl(url):
		fl=urllib.request.urlopen(url)
		#return '\n'.join(map(lambda x:x.decode("utf-8"),list(fl)))
		return fl.read()

	def loadxmlurl(url):
		return etree.fromstring(XMLService.loadfileurl(url))

class SASService(XMLService):
	def __init__(self):
		self.txml=None
		self.lunch=None
		self.dinner=None

	def _fetch(self):
		self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sas/ementas')

	def _validate(self):
		return True

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
		return True

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
	

a=SASService()
a.get()
print(a.lunch)


a=SACService()
a.get()
print(a.tickets)
