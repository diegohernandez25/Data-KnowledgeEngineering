import urllib.request, json
import abc
from lxml import etree
from BaseXClient import BaseXClient
import os.path
import time

#Global variables
_parentdir = os.path.dirname(os.path.abspath(__file__))

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
		self._validate()
		if not self._validate():
			raise Exception('XML not compliant')
		print("Valido")
		self._fillstruct()

	def loadfileurl(url,decode=0):
		fl=urllib.request.urlopen(url)
		return fl.read().decode() if decode else fl.read()

	def loadxmlurl(url,decode=0):
		return etree.fromstring(XMLService.loadfileurl(url,decode))

	def loadfile(filepath):
		return open(filepath, 'r').read().replace('\n', '')

	#allows to validate in xsd1.1
	def basexvalidate(inxml,style): #inxml=string, style=filepath
		session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
		try:
			session.execute('xquery validate:xsd('+inxml+',"'+style+'","1.1")')
			return True
		except:
			return False

class SASService(XMLService):
	def __init__(self):
		self.txml=None
		self.lunch=None
		self.dinner=None

	def _fetch(self):
		self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sas/ementas')

	def _validate(self):
		return etree.XMLSchema(etree.parse(_parentdir+'/SASServiceSchema.xsd')).validate(self.txml)

	def _fillstruct(self):
		self.lunch=dict()
		self.dinner=dict()
		for menu in self.txml.findall('.//menu'):
			if menu.attrib['disabled']!="0":
				continue

			entry=dict()
			for item in menu.findall('./items/item'):
				entry["".join(item.attrib['name'].split())]=item.text
				entry['name'] = menu.attrib['canteen']
			entry['weekday']=menu.attrib['weekday']
			if menu.attrib['meal']=='Almoço':
				#self.lunch[menu.attrib['canteen']]=menu.attrib['canteen']
				self.lunch[menu.attrib['canteen']]=entry
			elif menu.attrib['meal']=='Jantar':
				#self.dinner[menu.attrib['canteen']]=menu.attrib['canteen']
				self.dinner[menu.attrib['canteen']]=entry
			else:
				raise Exception('Unknown meal time')

		#print("LUNCH")
		#print(self.lunch)
		#print("DINNER")
		#print(self.dinner)

class SACService(XMLService):
	def __init__(self):
		self.txml=None
		self.tickets=None

	def _fetch(self):
		#self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sac/senhas/?date=2018-10-17&count=100')	
		self.txml=XMLService.loadxmlurl('http://services.web.ua.pt/sac/senhas')

	def _validate(self):
		return XMLService.basexvalidate(etree.tostring(self.txml).decode(),os.path.abspath(_parentdir+'/SACServiceSchema.xsd'))

	def _fillstruct(self):
		self.tickets=dict()
		if self.txml[0].attrib['count']=="0": #Closed
			return

		for ticket in self.txml.findall('./items/item'):
			letter=ticket.find('./letter').text
			if not letter in self.tickets:
				self.tickets[letter]={	'letter': ticket.find('.letter').text,\
										'name': ticket.find('./desc').text, \
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
		#TODO
		return etree.XMLSchema(etree.parse(_parentdir+'/UAParkingSchema.xsd')).validate(self.xml)
	
	def _fillstruct(self):
		self.parking = dict()
		for park in self.xml.findall('./Estacionamento'):
			self.parking[park.find('./ID').text] = {'Nome': park.find('./Nome').text,\
				'Latitude': park.find('./Latitude').text,\
				'Longitude': park.find('./Longitude').text,\
				'Capacidade':self.ltz(int(park.find('./Capacidade').text)),\
				'Ocupado': self.ltz(int(park.find('./Ocupado').text)),\
				'Livre': self.ltz(int(park.find('./Livre').text)),\
				'Color': self.color_status(int(park.find('./Ocupado').text),int(park.find('./Capacidade').text))}
		print(self.parking)

	def ltz(self,val):
		return 0 if val<0 else val

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

		_per = (float(occupied)/capacity)*100.0
		print(_per)
		if _per>90:
			return "#D87777"
		elif _per>75:
			return "#F4BC8B"
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
		return etree.XMLSchema(etree.parse(_parentdir+'/UANews.xsd')).validate(self.xml)

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

	def specific_fetch(self,dt = None,n = None, di = None, df = None, d=None, i =11,lid=1):
		url = 'https://uaonline.ua.pt/xml/contents_xml.asp?'
		print("Num of news: "+str(n))
		if(dt): url+='dt='+str(dt)+'&'
		if(di): url+='di='+di+'&'
		if(df): url+='df='+df+'&'
		if(d): url+='d='+str(d)+'&'
		if(n): url+='n='+str(n)+'&'
		if(url[len(url)-1]=='&'): url=url[:len(url)-1]
		print("Specific fetch url: "+ url)
		self.xml = etree.fromstring(bytes(bytearray(XMLService.loadfileurl(url))));
		#TODO: Validate
		if not self._validate():
			raise Exception('XML not compliant')

		self._fillstruct()

	def get_image(self, string, thumb = False):
		#TODO Image metadata has also valuable data that we may use if needed
		#print("image :"+string[string.find('https'):string.find('jpg')+ len('jpg')])
		_img_url= string[string.find('https'):string.find('jpg')+ len('jpg')] if thumb else\
		string[string.find('https'): string.find('_thumb')]+'.jpg'

		return "https://innapartments.com/inn-content/uploads/2016/11/aveiro-university-universidade-3-1024x576.jpg" if _img_url == ".jpg" else _img_url


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
		self._fetch()
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

class ScheduleMaker(XMLService):
	def __init__(self,in_xml):
		self.xml = in_xml
		self.schedules= list()
		self.daysarray=['segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira']
		self.dict= dict()
	def _fetch(self):
		pass
		#self.xml = etree.fromstring(self.in_xml)
	
	def _validate(self):
		return etree.XMLSchema(etree.parse(_parentdir+'/Cadeiras.xsd')).validate(self.xml)

	def _fillstruct(self):
		for opcao in self.xml.findall('.//cadeiras'):
			for cadeira in opcao.findall('.//cadeira'):
				for turma in cadeira.findall('.//turma'):
					aula = turma.find('./horarios/aula')
					_init_hour = float(aula.find('./inicio').text.split(':')[0]) 
					_fim_hour = float(aula.find('./fim').text.split(':')[0])
					_init_min = float(aula.find('./inicio').text.split(':')[1])
					_fim_min = float(aula.find('./fim').text.split(':')[1])
					t_init = _init_hour + (_init_min/100)
					t_fim = _fim_hour + (_fim_min/100)

					_dict={	'cadeira':cadeira.find('./nome').text,\
							'turno':turma.attrib['turno'],\
							'tipo':turma.attrib['tipo'],\
							'dia':aula.attrib['dia_da_semana'],\
							'sala':aula.find('./sala').text,\
							'inicio':aula.find('./inicio').text,\
							't_init':t_init,\
							'fim':aula.find('./fim').text,\
							't_fim':t_fim}
				
					if(aula.attrib['dia_da_semana'] not in self.dict.keys()): 
						self.dict[aula.attrib['dia_da_semana']]=[]
					self.dict[aula.attrib['dia_da_semana']].append(_dict)
			
			
			for day in self.daysarray:
				if day in self.dict.keys():
					self.dict[day] = sorted(self.dict[day], key=lambda k: k['t_init'])

			final_dict= dict()
			for day in self.daysarray:
				tmp_limit = 9.0
				tmp_end = 21.0
				tmp_list = []
				if day in self.dict.keys(): #Have classes on that day
					for elem_dict in self.dict[day]:
						_timestamp = self.calculate_timeoffset(elem_dict['t_init'],elem_dict['t_fim'])
						if(tmp_limit != elem_dict['t_init']):
							_off_timestamp = self.calculate_timeoffset(tmp_limit,elem_dict['t_init'])
							tmp_list.append(self.get_emptycolumn(_off_timestamp))
							tmp_limit=elem_dict['t_init']
						tmp_limit=elem_dict['t_fim']
						elem_dict['columns']=_timestamp
						tmp_list.append(elem_dict)

					##fill emptyness
					if(tmp_list[len(tmp_list)-1]['t_fim'] != tmp_end):
						_timestamp = self.calculate_timeoffset(tmp_list[len(tmp_list)-1]['t_fim'],tmp_end)
						tmp_list.append(self.get_emptycolumn(_timestamp))	
				else: #Does not have classes on that day
					_timestamp = self.calculate_timeoffset(tmp_limit,tmp_end)
					tmp_list.append(self.get_emptycolumn(_timestamp))
				
				final_dict[day] = tmp_list
				#print(final_dict[day])	
			#print("FINAL")
			#print(final_dict)
			self.schedules.append(final_dict)
			self.dict=dict()
		print(self.schedules[0])	
		print(self.schedules[1])	
	def calculate_timeoffset(self, start, end):
		_tmp = end - start
		if(int(_tmp*100)==30): 
			return 1
		_tmp = int(_tmp)*2 + (1 if _tmp%int(_tmp) else 0)
		return _tmp
	
	def get_emptycolumn(self, n):	
		return {'cadeira': None, 'turno': None, 'tipo': None, 'dia': None, 'sala': None, 'inicio': None, 't_init': None, 'fim': None, 't_fim': None, 'columns': n}

#a=ScheduleMaker(open('cadeiras.xml', 'r').read())
#a.get()
#print(a.schedules)
		

#a=SASService()
#a.get()
#print(a.lunch)
#print("Dinner")
#print(a.dinner)

#a=SACService()
#a.get()
#print(a.tickets)
#a = UAParking()
#a.get()
#print(a.parking)

#a = UANews()
#a.get()
#print(a.news)
