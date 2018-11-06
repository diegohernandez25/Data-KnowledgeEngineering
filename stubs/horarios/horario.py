from BaseXClient import BaseXClient
import os.path
from lxml import etree
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

    for uc in xml.findall('.//cadeira'):
        code = uc.attrib['codigo']
        codes.append(code)
        tipos_ucs[code] = tipo_aulas_uc(uc)
        for tipo in tipos_ucs[code]:
            if count_available_turmas(uc, tipo) == 1:
                turno = uc.find('.//turma[@tipo=\''+str(tipo)+'\']').attrib['turno']
                mandatory_classes.append((code, tipo, turno))

    call_gerar_horarios('local:create_tmp_horario("tmp.xml")')

    for i in range (1, 2):
        call_gerar_horarios('local:create_option(' + str(i) + ')')

        for uc in codes:
            call_gerar_horarios('local:append_cadeira_step1(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ')')
            call_gerar_horarios('local:append_cadeira_step2(' + str(i) + ', ' + str(uc) + ')')

        for (uc, tipo, turno) in mandatory_classes:
            call_gerar_horarios('local:append_turma(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ', "' + str(turno) + '")')
            tipos_ucs[uc].remove(tipo)

        for uc in codes:
            for tipo in tipos_ucs[uc]:
                turmas = xml.findall('.//turma[@tipo=\''+str(tipo)+'\']')
                for t in turmas:
                    current = etree.fromstring(call_gerar_horarios('local:get_current_horario()'))
                    flag = call_gerar_horarios('local:fits_horario(' + str(i) + ', ' + str(uc) + ', "' + str(t.attrib['turno']) + '")')
                    if flag == "true":
                        call_gerar_horarios(
                            'local:append_turma(' + str(i) + ', ' + str(curso) + ', ' + str(uc) + ', "' + str(t.attrib['turno']) + '")')
                        break

def tipo_aulas_uc(uc):
    tipo = []
    for n in uc.findall('.//turma'):
        tipo.append(n.attrib['tipo'])
    return set(tipo)

def count_available_turmas(uc, uc_type):
    turnos = uc.findall('.//turma[@tipo=\''+str(uc_type)+'\']')
    return len(turnos)

gerar_horarios(8240, 4)
call_gerar_horarios('local:delete_tmp_horario()')