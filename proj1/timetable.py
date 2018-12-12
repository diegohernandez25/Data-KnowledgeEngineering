import itertools

def combine_courses(courses):
    entries = []
    options = []
    for c in courses:
        comb = list(itertools.product(*courses[c]))
        local = []
        for e in comb:
            local.append([c, e])
        print(comb)
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

    timetable = []

    for e in entries:
        for entry in e:
            if entry not in timetable:
                timetable.append(entry)
    for t in timetable:
        print(t)
    print(len(timetable))
    return timetable




courses = dict()
courses["ACA"] = [["P1", "P2", "P3", "P4"], ["T1"], ["OT1"]]
courses["ARA"] = [["P1", "P2", "P3", "P4"], ["T1"]]
courses["CV"] = [["P1", "P2", "P3"], ["T1"]]
courses["EDC"] = [["P1", "P2", "P3"], ["T1"]]
courses["SEG"] = [["P1", "P2", "P3"], ["T1"]]

#print(courses)
combine_courses(courses)
