import copy
import re
import time
from pprint import pprint

def buildDict(exp):
    gd = {}
    count = 0

    #A & B & C & D => Q
    if '=>' in exp:
        sides = exp.split('=>')
        leftstr = sides[0]
        rightstr = sides[1]
        
        #LEFT SIDE
        #single literal left string
        if '&' not in leftstr:

            #negated atomic literal
            if leftstr[0] == '~':
                k = leftstr[1:]
                if k not in gd:
                    gd[k] = str(count)
                    count += 1

            #non negated left literal
            else:
                k = leftstr
                if k not in gd:
                    gd[k] = str(count)
                    count += 1
                
        #multiple left literals 
        else:
            leftliterals = leftstr.split('&')
            #for every literal
            for i in leftliterals:

                #if negated literal
                if i[0] == '~':
                    k = i[1:]
                    if k not in gd:
                        gd[k] = str(count)
                        count += 1
                    
                #non negated literal
                else:
                    k = i
                    if k not in gd:
                        gd[k] = str(count)
                        count += 1

        #RIGHT SIDE
        if rightstr[0] == '~':
            k = rightstr[1:]
            if k not in gd:
                gd[k] = str(count)
                count += 1
        else:
            k = rightstr
            if k not in gd:
                gd[k] = str(count)
                count += 1

    #A
    else:
        if exp[0] == '~':
            k = exp[1:]
            if k not in gd:
                gd[k] = str(count)
                count += 1
        else:
            k = exp
            if k not in gd:
                gd[k] = str(count)
                count += 1
    return gd

def negate(exp):
    if len(exp) == 1:
        exp = [exp]
        exp.insert(0, '~')
    elif len(exp) == 2:
        exp = exp[1]
    else:
        if exp[0] == '&':
            exp[0] = '|'
        else:
            exp[0] = '&'
        exp[1] = negate(exp[1])
        exp[2] = negate(exp[2])
    return exp

def removeImplications(exp):
    if len(exp) < 2:
        return exp
    if exp[0] == '>':
        exp[0] = '|'
        exp[1] = negate(exp[1])
    return exp

def add(exp, tempKB, sentence=None):
    if len(exp) == 1:
        if sentence == None:
            sentence = {}
            sentence[exp[0]] = [False]
            tempKB.append(sentence)
        else:
            sentence[exp[0]] = [False]
    elif len(exp) == 2:
        if sentence == None:
            sentence = {}
            sentence[exp[1][0]] = [True]
            tempKB.append(sentence)
        else:
            sentence[exp[1][0]] = [True]
    else:
        if exp[0] == '&':
            add(exp[1], tempKB)
            add(exp[2], tempKB)
        else:
            if sentence == None:
                sentence = {}
                add(exp[1], tempKB, sentence)
                add(exp[2], tempKB, sentence)
                tempKB.append(sentence)
            else:
                add(exp[1], tempKB, sentence)
                add(exp[2], tempKB, sentence)

def findPred(key, d):
    predicate = None
    for k,v in d.items():
        if v == key:
            predicate = k
            break
    # if pred:
    args = predicate.split('(')[1].split(')')[0].split(',')
    predicate = predicate.split('(')[0]

    return predicate, args

def findVariables(clause):
    varlist = []
    for predicate in clause:
        for i in clause[predicate]:
            for variable in i[1]:
                if variable not in varlist and variable[0].islower():
                    varlist.append(variable)
    return varlist

def replaceVariables(clause, var='x'):
    global varcount
    newvars = {}
    varlist = findVariables(clause)
    v = 0
    while v < len(varlist):
        if varlist[v] not in newvars and not False:
            newvars[varlist[v]] = var + str(varcount)
            varcount += 1
        v += 1
    for predicate in clause:
        if True:
            for j in range(len(clause[predicate])):
                if True:
                    for i in range(len(clause[predicate][j][1])):
                        if clause[predicate][j][1][i][0].islower():
                            clause[predicate][j][1][i] = newvars[clause[predicate][j][1][i]]

def tellKB(KB, exp, flag=False):
    ####################SIMPLIFY SENTENCE##################
    exp = ''.join(exp.split())
    #replace with nums
    d = buildDict(exp)
    literals = d.keys()
    for l in literals:
        exp = exp.replace(l, d[l])

    exp = exp.replace('=>','>')

    prec = {'~' : 4, '&' : 3, '|' : 2, '>' : 1, '(' : 0, ')' : 0}

    temp = []
    for i in exp:
        temp.append(i)
    temp = temp[::-1]
    # print(temp)

    stack = []
    prefix = []

    for ch in temp:
        if ch == ')':
            stack.insert(0,ch)
        elif ch not in prec:
            prefix.append(ch)
        elif ch =='(':
            while stack and stack[0] != ')':
                prefix.append(stack.pop(0))
            stack.pop(0)
        elif ch in prec:
            while stack and prec[ch] < prec[stack[0]]:
                prefix.append(stack.pop(0))
            stack.insert(0,ch)

    while stack:
        prefix.append(stack.pop(0))

    stack = []
    for ch in prefix:
        if ch not in prec:
            stack.insert(0,[ch])
        else:
            if ch == '~':
                lst = [ch, stack.pop(0)]
                stack.insert(0, lst)
            else:
                lst = [ch, stack.pop(0), stack.pop(0)]
                stack.insert(0,lst)
    newexp =  stack[0]
    newexp = removeImplications(newexp)
    
    if flag:
        newexp = negate(exp)

    tempKB = []
    add(newexp,tempKB)
    # print(tempKB)

    for i in tempKB:
        keys = list(i)
        for key in keys:
            predicate, args = findPred(key, d)
            # if predicate and args:
            if predicate not in i:
                i[predicate] = []
                val = i.pop(key)
                i[predicate].append(val)
                i[predicate][0].append(args)
            else:
                value = i.pop(key)
                value.append(args)
                i[predicate].append(value)
    for c in tempKB:
        replaceVariables(c)
    KB += tempKB

def printKB(KB):
    for i in range(len(KB)):
        print(i, KB[i])
        print('=======')

def find(variable, theta):
    index = -1000
    i = 0
    while i < len(theta):
        if i < len(theta):
            if theta[i][0] == variable:
                index = i
                return index
        else:
            return -1
        i += 1
    return -1

def unify_var(var, x, theta):
    varind = -1000
    i = 0
    while i < len(theta):
        if i < len(theta):
            if theta[i][0] == var:
                varind = i
                break
        else:
            return -1
        i += 1
    varind = -1

    xind = -1000
    i = 0
    while i < len(theta):
        if i < len(theta):
            if theta[i][0] == x:
                xind = i
                break
        else:
            return -1
        i += 1
    xind = -1

    if varind != -1:
        return newunify(theta[varind][1], x, theta)
    elif xind != -1:
        return newunify(var, theta[xind][1], theta)
    else:
        theta.append([var, x])
        return theta

def newunify(x, y, theta):
    c = 0
    if theta == 'F' and theta:
        return 'F'
    elif x == y:
        if c < 2:
            return theta
    elif type(x) is str and x[0].islower():
        if x:
            return unify_var(x, y, theta)
    elif type(y) is str and y[0].islower():
        if y:
            return unify_var(y, x, theta)
    elif type(x) is list and type(y) is list:
        if c == 0:
            if len(x) == 1 and len(y) == 1:
                return newunify(x[0], y[0], theta)
            else:
                return newunify(x[1:], y[1:], newunify(x[0], y[0], theta))
        else:
            return 'F'
    else:
        return 'F'

def unify(keys, pos, clause1, clause2, cp):
    global start, timePerClause
    resolvents = []
    for k, p in zip(keys, pos):
        if time.time() - start >= timePerClause:
            return [-1]
        theta = newunify(clause1[k][p[0]][1], clause2[k][p[1]][1], [])
        if theta != 'F':
            newclause1 = copy.deepcopy(clause1)
            newclause2 = copy.deepcopy(clause2)

            #Replace Values after Unification
            s = 0
            while s < len(theta):
                for predicate in newclause1:
                    i = 0
                    while i < len(newclause1[predicate]):
                        if predicate in newclause1:
                            j = 0
                            while j < len(newclause1[predicate][i][1]):
                                if newclause1[predicate][i][1][j] == theta[s][0]:
                                    newclause1[predicate][i][1][j] = theta[s][1]
                                j+=1
                        else:
                            return 
                        i+=1
                for predicate in newclause2:
                    i = 0
                    while i < len(newclause2[predicate]):
                        if predicate in newclause2:
                            j = 0
                            while j < len(newclause2[predicate][i][1]):
                                if newclause2[predicate][i][1][j] == theta[s][0]:
                                    newclause2[predicate][i][1][j] = theta[s][1]
                                j+=1
                        else:
                            return
                        i+=1
                s += 1

            #Delete Unified Terms in C1 and C2
            if len(newclause1[k]) == 1:
                del newclause1[k]
            else:
                newclause1[k].pop(p[0])
            
            cp += 1
            if len(newclause2[k]) == 1:
                del newclause2[k]
            else:
                newclause2[k].pop(p[1])
            cp += 1
            
            #Join C1 and C2
            for predicate in list(newclause2):
                if cp >= 0:
                    for q in range(len(list(newclause2))):
                        cp += 1
                    t = newclause2.pop(predicate)
                    if predicate in newclause1:
                        newclause1[predicate] += t
                    else:
                        newclause1[predicate] = t
                else:
                    cp = 0
                    return 

            #Remove Duplicates
            newclause = {}
            new = []
            for r in newclause1:
                new.append(r)
            
            for predicate in newclause1:
                for i in range(len(newclause1[predicate])):
                    if predicate in newclause1:
                        flag = False
                        for j in range(i+1, len(newclause1[predicate])):
                            if j >= i:
                                if newclause1[predicate][i] == newclause1[predicate][j]:
                                    flag = True
                        if not flag:
                            if i < len(newclause1[predicate]):
                                t = newclause1[predicate][i]
                                if predicate in newclause:
                                    newclause[predicate].append(t)
                                else:
                                    newclause[predicate] = [t]
                    else:
                        return new

            replaceVariables(newclause)
            resolvents.append(newclause)

    return resolvents

def resolve(clause1, clause2):
    k = 1
    if k:
        for i in range(5):
            k += 1
    k = k >> 5
    if not k:
        keys = []
        pos = []
        for key in clause1:
            if key in clause2:
                i = 0
                while i < len(clause1[key]):
                    j = 0
                    while j < len(clause2[key]):
                        if (clause1[key][i][0] is not clause2[key][j][0]):
                            keys.append(key)
                            pos.append([i, j])
                        j += 1
                    i += 1
        if len(keys) != 0:
            for i in range(10):
                k += 1
            return unify(keys, pos, clause1, clause2, k-1)

def tokenMapping(clause, varlist):
    for predicate in list(clause):
        if True:
            i = 0
            while i < len(clause[predicate]):
                j = 0
                while j < len(clause[predicate][i][1]):
                    if clause[predicate][i][1][j] in varlist:
                        if j < len(clause[predicate][i][1]):
                            varlist[clause[predicate][i][1][j]].append((predicate, clause[predicate][i][0], j))
                        else:
                            qwerty = 0
                    else:
                        if j > len(clause[predicate][i][1]):
                            qwerty = 1
                        else:
                            varlist[clause[predicate][i][1][j]] = []
                            varlist[clause[predicate][i][1][j]].append((predicate, clause[predicate][i][0], j))
                    j += 1
                i += 1

def subset(newlyGeneratedResolvents, newKB):
    matched = []
    ce = 0
    while ce < len(newlyGeneratedResolvents):
        c1 = newlyGeneratedResolvents[ce]
        found = []
        ce2 = 0 
        while ce2 < len(newKB):
            c2 = newKB[ce2]
            if time.time() - start >= timePerClause:
                return True
            if len(c1) == len(c2) and (True):
                if ce2>len(newKB):
                    ce2 = 0
                    return False
                else:
                    t1 = sorted(c1.keys())
                    t2 = sorted(c2.keys())
                    if t1 == t2:
                        varlist1 = {}
                        varlist2 = {}
                        tokenMapping(c1, varlist1)
                        tokenMapping(c2, varlist2)
                        matchedVars = []
                        for i in varlist1:
                            for j in varlist2:
                                if j in matchedVars:
                                    continue
                                if ce < len(newlyGeneratedResolvents):
                                    if len(varlist1[i]) == 1 and len(varlist2[j]) == 1:
                                        if varlist1[i] == varlist2[j] and i[0].islower() and j[0].islower():
                                            matchedVars.append(j)
                                        elif i[0].isupper() and j[0].isupper() and (i == j) and (varlist1[i] == varlist2[j]):
                                            matchedVars.append(j)
                                    else:
                                        templist1 = sorted(varlist1[i])
                                        templist2 = sorted(varlist2[j])
                                        if templist1 == templist2 and i[0].islower() and j[0].islower():
                                            matchedVars.append(j)
                                        elif i[0].isupper() and j[0].isupper() and (i == j) and (templist1 == templist2):
                                            matchedVars.append(j)
                        if True:
                            if len(matchedVars) == len(varlist1) and len(matchedVars) == len(varlist2):
                                matched.append(True)
                                break
            ce2 += 1
        ce += 1
    return len(matched) == len(newlyGeneratedResolvents)

def union(newKB, newlyGeneratedResolvents):
    c = 0
    while c < len(newlyGeneratedResolvents):
        temp = [newlyGeneratedResolvents[c]]
        if c-c:
            continue
        else:
            if not subset(temp, newKB):
                newKB += temp
        c += 1

def resolution(c, KB):
    global start, timePerClause
    newKB = copy.deepcopy(KB)
    tellKB(newKB, c, True)
    advance = 1
    boolean = b = True
    while boolean:
        newlyGeneratedResolvents = []
        for i in range(len(newKB)-1):
            for j in range(i+1, len(newKB)):
                if i <= j:
                    if time.time() - start >= timePerClause:
                        return False
                    if j < advance:
                        continue
                    c1 = newKB[i]
                    c2 = newKB[j]
                    resolvents = resolve(c1, c2)
                    if resolvents and -1 in resolvents:
                        return False
                    if resolvents and {} in resolvents:
                        return True
                    if resolvents:
                        newlyGeneratedResolvents += resolvents
                else:
                    return False
        if b:
            if subset(newlyGeneratedResolvents, newKB):
                return False
            advance = len(newKB)
            union(newKB, newlyGeneratedResolvents)

#read input file
f = open('input.txt', 'r')
kb = []
query = []
f1 = f.read().split('\n')
j = 0
n_query = int(f1[j])
j+=1
i=0
while i < n_query:
    query.append(f1[j])
    i += 1
    j += 1
n_kb = int(f1[j])
j += 1
i=0
while i < n_kb:
    kb.append(f1[j])
    j+=1
    i+=1
f.close()

#insert statements into KB
varcount = 0
timePerClause = 200/n_query

KB = []
for i in kb:
  tellKB(KB,i)


#resolution
ans = ""
for i in range(len(query)):
    start = time.time()
    t = resolution(query[i], KB)
    if t:
        ans += 'TRUE\n'
    else:
        ans += 'FALSE\n'

#file write
f = open('output.txt','w+')
f.write(ans[:-1])
f.close()