from BaseXClient import BaseXClient
import os.path
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

def call_gerar_horarios(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'generate_horarios.xq'), 'r').read()+'\n'+func)

def call_gerar_reservas(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'horariofunc.xq'), 'r').read()+'\n'+func)
