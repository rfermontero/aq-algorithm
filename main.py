#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys


def defineLef():
    return (1, 2)  # (min cobertura, max premisas)


def getComplexInEntry(val):
    return list(val)


def checkLef(l, lef, positives, seed):
    minCobert = lef[0]
    maxPremis = lef[1]
    # Comprobamos que tiene maximo de premisas
    if len(l) > 0 and len(getComplexInEntry(l[0])) >= maxPremis:
        print("La función LEF no permite más de " + str(maxPremis) +
              " premisas, por lo que se descarta cualquier especialización.")
        return False
    # Comprobamos que cumple minimo de positivias
    cobert = 0
    for positive in positives:
        complexList = getComplexInEntry(l[0])
        isCobering = True
        for c in complexList:
            if cobert >= minCobert:
                break
            if positive[int(c)] != list(seed.values())[int(c)]:
                isCobering = False
                break
            if isCobering:
                cobert += 1

    if cobert < minCobert:
        print("No cubre el minimo de positivos para continuar especializando")
        return False

    return True


def applyLef(star, lef, positives, seed, columns):
    maxP = sys.maxsize
    minC = 0
    res = ""
    for e in star:
        cober = 0
        premises = len(getComplexInEntry(e))
        for positive in positives:
            complexList = getComplexInEntry(e)
            isCobering = True
            for c in complexList:
                if positive[int(c)] != list(seed.values())[int(c)]:
                    isCobering = False
                    break
            if isCobering:
                cober += 1
        sys.stdout.write("C"+str(e)+" ")
        for lefR in getComplexInEntry(e):
            sys.stdout.write(str(columns[int(lefR)])+"="+str(seed.get(
                columns[int(lefR)]))+" ")

        print("--> cobertura="+str(cober)+" premisas="+str(premises))
        if cober >= lef[0] and premises <= lef[1]:
            if cober > minC and premises <= maxP:
                minC = cober
                maxP = premises
                res = e
    print("Nos quedamos con " + " C"+str(res) + " " +
          str(columns[int(res)])+"="+str(seed.get(columns[int(res)])))
    return res


def readCsv():
    result = {}
    result["examples"] = []
    with open('input.csv') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        columns = True
        for row in reader:
            if columns:
                result["columns"] = row
                columns = False
            else:
                result["examples"].append(row)
    return result


def getPositives(values):
    return [example for example in values['examples'] if example[len(example)-1] == 'si']


def getNegatives(values):
    return [example for example in values['examples'] if example[len(example)-1] == 'no']


def getLPrime(columns, search, negatives):
    columnIndex = columns.index(search[0])
    isInLPrime = False
    for negative in negatives:
        if negative[columnIndex] == search[1]:
            isInLPrime = True
            print("C"+str(columnIndex)+"=("+str(search[0])+"="+str(search[1]) +
                  ") -> Cubre ejemplos negativos. Hay que especializar")
            break
    if not isInLPrime:
        print("C"+str(columnIndex)+"=("+str(search[0])+"="+str(search[1]) +
              ") -> Ok pasa a estrella")
    return isInLPrime


def getLAndStar(seed, negatives, values):
    l = []
    star = []
    for entry in seed.items():
        if entry[0] != 'clase':
            if getLPrime(values["columns"], entry, negatives):
                l.append(str(values["columns"].index(entry[0])))
            else:
                star.append(str(values["columns"].index(entry[0])))
    return (star, l)


def especializeL(seed, negatives, star, l):
    passeds = dict()
    lPrime = []
    e = []
    for lEntry in l:
        for index, seedEntry in enumerate(seed.items()):
            if index == len(seed.items()) - 1:
                break

            if int(lEntry) in passeds.get(str(index), []):
                print("C"+str(lEntry)+str(index) +
                      ' Ya estudiado al contrario')
            elif str(lEntry) == str(index):
                print("C"+str(lEntry)+str(index) +
                      " Se descarta, es el mismo ejemplo")
            elif str(index) in star:
                print("C"+str(lEntry)+str(index) +
                      " Se descarta, elemento ya en estrella")
            else:
                isInLPrime = False
                for negative in negatives:
                    if negative[int(lEntry)] == list(seed.values())[int(lEntry)] and negative[index] == seedEntry[1]:
                        print(
                            "C"+str(lEntry)+str(index)+" Cubre ejemplos negativos. Hay que especializarlo")
                        lPrime.append(str(lEntry)+str(index))
                        isInLPrime = True
                if not isInLPrime:
                    print("C"+str(lEntry)+str(index)+" ok, pasa a la estrella")
                    e.append(str(lEntry)+str(index))
            passeds[lEntry] = passeds.get(lEntry, [])+[index]
    return (e, lPrime)


def aq(values, lef):
    print("E = C: cualquier hipótesis es si")
    print("L = [()]")
    print("Separamos ejemplos positivos y negativos")
    r = []
    rs = dict()
    e = []
    positives = getPositives(values)
    negatives = getNegatives(values)
    print("Positivos: " + str(positives))
    print("Negativos: " + str(negatives))
    print("Procesamos los ejemplos positivos")

    matchesIndex = []
    while positives:
        if len(rs) > 0:
            for index, positive in enumerate(positives):
                for rsCondIndex in range(len(rs.keys())):
                    rsKey = list(rs.keys())[rsCondIndex]
                    rsValues = rs[rsKey]
                    shouldMatch = len(rsValues)
                    match = 0
                    for rsValue in rsValues:
                        if positives[index][int(rsKey)] == rsValue:
                            match += 1
                    if shouldMatch == match:
                        matchesIndex.append(index)
        if len(r) > 0:
            sys.stdout.write(
                "Eliminamos los ejemplos de la lista positiva que cubren R=")
            for result in rs.items():
                for res in result[1]:
                    sys.stdout.write("("+values["columns"]
                                     [int(result[0])]+"="+str(res)+") ")
            print("")
        nPositives = [i for j, i in enumerate(
            positives) if j not in set(matchesIndex)]
        positives = nPositives[:]

        if len(positives) > 0:

            positive = positives[0]
            seed = dict(zip(values["columns"], positive))
            seed.pop("clase")
            print("S: " + str(seed))

            res = getLAndStar(seed, negatives, values)
            lPrime = res[1]
            e = res[0]

            print("E="+str(e))
            print("L'="+str(lPrime))
            print("L=L'")
            print('')

            print("Comprobamos si se puede especializar aplicando lef")
            while len(lPrime) != 0 and checkLef(lPrime, lef, positives, seed) is True:
                espe = especializeL(seed, negatives, e, lPrime)
                lPrime = espe[1]
                e = e + espe[0]
                print("E="+str(e))
                print("L'="+str(lPrime))
                print("L=L'")
                print("Se aplica la función LEF a los complejos de la estrella para elegir aquel que pasará a formar parte del recubrimiento")
                lefResult = applyLef(
                    e, lef, positives, seed, values["columns"])
                r.append(lefResult)
                for lefR in getComplexInEntry(lefResult):
                    rs[lefR] = rs.get(lefR, []) + \
                        [list(seed.values())[int(lefR)]]
            sys.stdout.write("R=")
            for result in rs.items():
                for res in result[1]:
                    sys.stdout.write("("+values["columns"]
                                     [int(result[0])]+"="+str(res)+") ")
            print("")
    print("Solucion: ")
    for result in rs.items():
        for res in result[1]:
            sys.stdout.write(values["columns"]
                             [int(result[0])]+"="+str(res)+" ")
    print("")


values = readCsv()
lef = defineLef()
aq(values, lef)
