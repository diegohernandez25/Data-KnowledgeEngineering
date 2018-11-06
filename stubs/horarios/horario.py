from lxml import etree
from BaseXClient import BaseXClient
import os.path

from lxml import etree
from time import strptime,strftime
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')



def call_gerar_horarios(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'generate_horarios.xq'), 'r').read()+'\n'+func)

def call_gerar_reservas(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'horariofunc.xq'), 'r').read()+'\n'+func)



def gerar_horarios(curso, ano):
    ucs = call_gerar_horarios('local:get_ucs_ano(' + str(curso) + ', ' + str(ano) + ')')
    xml = etree.fromstring(ucs)
    tipos_ucs = dict()
    mandatory_classes = []
    codes = []
    escolhas = dict()

    for uc in xml.findall('.//cadeira'):
        code = uc.attrib['codigo']
        codes.append(code)
        tipos_ucs[code] = tipo_aulas_uc(uc)
        for tipo in tipos_ucs[code]:
            if count_available_turmas(uc, tipo) == 1:
                turno = uc.find('.//turma[@tipo=\''+str(tipo)+'\']').attrib['turno']
                mandatory_classes.append((code, tipo, turno))

    call_gerar_horarios('local:create_tmp_horario("tmp.xml")')


    for i in range (0, len(codes)):
        call_gerar_horarios('local:create_option(' + str(i) + ')')
        for uc in codes:
            print("DEBG: i:" + str(i) + " curso:" + str(curso)+ " uc:" + str(uc))
            call_gerar_horarios('local:append_cadeira_step1(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ')')
            call_gerar_horarios('local:append_cadeira_step2(' + str(i) + ', ' + str(uc) + ')')

        for (uc, tipo, turno) in mandatory_classes:
            call_gerar_horarios('local:append_turma(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ', "' + str(turno) + '")')
            if i==0:
                tipos_ucs[uc].remove(tipo)

        tmp = codes.pop(0)
        codes.append(tmp)
        print(codes)
        for uc in codes:
            print(uc)
            for tipo in tipos_ucs[uc]:
                tmp = etree.fromstring(call_gerar_horarios('local:get_uc(' + str(uc) + ', ' + str(curso) + ')'))
                turmas = tmp.findall('.//turma[@tipo=\''+str(tipo)+'\']')
                for t in turmas:
                    flag = call_gerar_horarios('local:fits_horario(' + str(i) + ', ' + str(uc) + ', "' + str(t.attrib['turno']) + '")')
                    if flag == "true":


                        print("attempt: uc:" + str(uc) + " turno:" +  str(t.attrib['turno']))
                        call_gerar_horarios(
                            'local:append_turma(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ', "' + str(t.attrib['turno']) + '")')
                        break

    gerados = etree.fromstring(call_gerar_horarios('local:get_current_horario()'))
    print(etree.tostring(gerados).decode())
    return gerados

def tipo_aulas_uc(uc):
    tipo = []
    for n in uc.findall('.//turma'):
        tipo.append(n.attrib['tipo'])
    return set(tipo)

def count_available_turmas(uc, uc_type):
    turnos = uc.findall('.//turma[@tipo=\''+str(uc_type)+'\']')
    return len(turnos)


#print(etree.tostring(gerar_horarios(8295, 1)).decode())
#call_gerar_horarios('local:delete_tmp_horario()')


def _reg_time(time):
	return strftime("%H:%M:%S",strptime(time,"%H:%M"))

#returns a list of strings
def listar_salas_livres(inicio,fim,dia):
	xml=etree.fromstring(call_gerar_reservas('local:get_salas_livres(xs:time("'+_reg_time(inicio)+'"),xs:time("'+_reg_time(fim)+'"),xs:date("'+dia+'"))'))
	ret=list()
	for el in xml.findall('.//sala'):
		ret.append(el.text)
	return ret

def sala_reservada(sala,inicio,fim,dia):
	return call_gerar_reservas('local:sala_reservada("'+sala+'",xs:time("'+_reg_time(inicio)+'"),xs:time("'+_reg_time(fim)+'"),xs:date("'+dia+'"))')=="true"

#returns true on success
def reservar_sala(nmec,sala,inicio,fim,dia):
	before=sala_reservada(sala,inicio,fim,dia)
	call_gerar_reservas('local:reservar_sala('+str(nmec)+',"'+sala+'",xs:time("'+_reg_time(inicio)+'"),xs:time("'+_reg_time(fim)+'"),xs:date("'+dia+'"))')
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
#print(listar_salas_livres("07:00","20:00","2018-11-05"))
#print(reservar_sala(12345,"04.1.02","23:00:00","23:30:00","2018-11-05"))
