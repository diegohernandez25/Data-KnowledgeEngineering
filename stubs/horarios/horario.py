from lxml import etree
from BaseXClient import BaseXClient
import os.path
import itertools
from lxml import etree
from time import strptime,strftime
session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')



def call_gerar_horarios(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'generate_horarios.xq'), 'r').read()+'\n'+func)

def call_gerar_reservas(func):
	return session.execute('xquery \n'+open(os.path.join(os.path.dirname(__file__), 'horariofunc.xq'), 'r').read()+'\n'+func)



def gerar_horarios(curso, ano):
    call_gerar_horarios('local:create_tmp_horario("tmp.xml")')
    ucs = call_gerar_horarios('local:get_ucs_ano(' + str(curso) + ', ' + str(ano) + ')')
    xml = etree.fromstring(ucs)

    pipelin = courses_to_xml(combine_courses(xml_to_courses(xml)), curso)

    gerados = etree.fromstring(call_gerar_horarios('local:get_current_horario()'))

    call_gerar_horarios('local:delete_tmp_horario()')

    f = open("filetest.xml", "w")
    f.write(etree.tostring(gerados).decode())
    return gerados


def tipo_aulas_uc(uc):
    tipo = []
    for n in uc.findall('.//turma'):
        tipo.append(n.attrib['tipo'])
    return list(set(tipo))



def xml_to_courses(ucs):
    courses = ucs.findall(".//cadeira")
    entries = dict()
    for c in courses:
        code = c.attrib['codigo']
        entries[code] = xml_to_course(c)

    return entries

def xml_to_course(course):
    tipos = tipo_aulas_uc(course)
    turmas = course.findall(".//turma")
    struct = dict()

    for t in tipos:
        if t != "OT":
            struct[t] = []

    for t in turmas:
        if t.attrib["tipo"] != "OT":
            if len(struct[t.attrib["tipo"]]) < 4 :
                struct[t.attrib["tipo"]].append(t.attrib["turno"])

    ret = []
    for e in struct:
        ret.append(struct[e])
    return ret

def courses_to_xml(courses, curso_id):
    i = 0
    count = 0
    for c in courses:
        call_gerar_horarios('local:create_option(' + str(i) + ')')

        possible = course_to_xml(c, i, curso_id)
        if possible:
            count+=1
        if count > 7:
            break;
        i+=1

def course_to_xml(course, i, curso_id):
    del_option = False
    for c in course:
        uc = c[0]

        call_gerar_horarios('local:append_cadeira_step1(' + str(i) + ', ' + str(curso_id) + ', ' + str(uc) + ')')
        call_gerar_horarios('local:append_cadeira_step2(' + str(i) + ', ' + str(uc) + ')')

        for e in c[1]:
            turma_val = e
            turma_xml = call_gerar_horarios('local:get_turma(' + str(uc) + ', ' + str(curso_id) + ', \'' + str(turma_val) + '\')')
            flag = call_gerar_horarios('local:fits_horario(' + str(i) + ', ' + str(uc) + ', "' + str(etree.fromstring(turma_xml).attrib['turno']) + '")')
            if flag == "true":
                call_gerar_horarios('local:append_turma(' + str(i) + ', ' + str(curso_id) + ', ' + str(uc) + ', "' + str(etree.fromstring(turma_xml).attrib['turno']) + '")')
            else:
                del_option = True
                break;
        if del_option:
            call_gerar_horarios('local:del_option(' + str(i) + ')')
            break
    return not del_option

def combine_courses(courses):
    entries = []
    options = []
    for c in courses:
        comb = list(itertools.product(*courses[c]))
        local = []
        for e in comb:
            local.append([c, e])
        options.append(local)

    for i in range (0, len(options)):
        for course in options[i]:
            tmp = []
            for o in options:
                tmp.append(o.copy())
            rmv = []

            for e in tmp[i]:
                if course[0] == e[0] and course != e:
                    rmv.append(e)

            for r in rmv:
                tmp[i].remove(r)

            if len(courses) == 2:
                entries.append(list(itertools.product(tmp[0], tmp[1])))
            elif len(courses) == 3:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2])))
            elif len(courses) == 4:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2], tmp[3])))
            elif len(courses) == 5:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4])))
            elif len(courses) == 6:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])))
            elif len(courses) == 7:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6])))
            elif len(courses) == 5:
                entries.append(list(itertools.product(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6], tmp[7])))

    timetable = []
    i=0

    for e in entries:
        i+=1
        for entry in e:
            if entry not in timetable:
                timetable.append(entry)

    return timetable

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
