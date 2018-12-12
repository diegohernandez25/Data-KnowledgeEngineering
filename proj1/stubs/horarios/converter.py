from BaseXClient import BaseXClient
import os.path

infile=os.path.abspath('Horarios_Cursos_DETI.html')
style=os.path.abspath('convert.xsl')

session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
print(session.execute('xquery xslt:transform(html:parse(file:read-text("'+infile+'")),"'+style+'")'))
