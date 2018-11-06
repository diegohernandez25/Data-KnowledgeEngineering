from lxml import etree
from BaseXClient import BaseXClient
import os.path
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

def call_gerar_horarios(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'generate_horarios.xq'), 'r').read()+'\n'+func)

def call_gerar_reservas(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'horariofunc.xq'), 'r').read()+'\n'+func)


#returns a list of strings
def listar_salas_livres(inicio,fim,dia):
	xml=etree.fromstring(call_gerar_reservas('local:get_salas_livres(xs:time("'+inicio+'"),xs:time("'+fim+'"),xs:date("'+dia+'"))'))
	ret=list()
	for el in xml.findall('.//sala'):
		ret.append(el.text)
	return ret

def sala_reservada(sala,inicio,fim,dia):
	return call_gerar_reservas('local:sala_reservada("'+sala+'",xs:time("'+inicio+'"),xs:time("'+fim+'"),xs:date("'+dia+'"))')=="true"

#returns true on success
def reservar_sala(nmec,sala,inicio,fim,dia):
	before=sala_reservada(sala,inicio,fim,dia)
	call_gerar_reservas('local:reservar_sala('+str(nmec)+',"'+sala+'",xs:time("'+inicio+'"),xs:time("'+fim+'"),xs:date("'+dia+'"))')
	return not before and sala_reservada(sala,inicio,fim,dia)

#returns list of (sala,inicio,fim)
def get_reservas(nmec,dia):
	print(call_gerar_reservas('local:get_reservas('+str(nmec)+',xs:date("'+dia+'"))'))
	xml=etree.fromstring(call_gerar_reservas('local:get_reservas('+str(nmec)+',xs:date("'+dia+'"))'))
	ret=list()
	for el in xml:
		ret.append((el.attrib['sala'],el.attrib['inicio'],el.attrib['fim']))
	return ret

#print(get_reservas(12345,"2018-11-05"))
#print(listar_salas_livres("17:00:00","20:00:00","2018-11-05"))
#print(reservar_sala(12345,"04.1.02","23:00:00","23:30:00","2018-11-05"))
