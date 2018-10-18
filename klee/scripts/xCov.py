#!/usr/bin/python

from __future__ import division
from optparse import OptionParser

import sys, os

#global vars
instIndex=5;

def getFuncCov(input, opts):
    inputs = [[None, iter(open(input))]]
    def getLine(elt):
        la,i = elt
        if la is None:
            try:
                ln = i.next()
            except StopIteration:
                ln = None
            except:
                raise ValueError("unexpected IO error")
            return ln
        else:
            elt[0] = None
            return la
    def getLines():
        return map(getLine,inputs)
    def putback(ln,elt):
        assert elt[0] is None
        elt[0] = ln

    events = None
    
    # read header (up to ob=)
    while 1:
        lns = getLines()
        ln = lns[0]
        if ln.startswith('ob='):
            break
        else:
            if ln.startswith('positions:'):
                if ln!='positions: instr line\n':
                    raise ValueError("unexpected 'positions' directive")
            elif ln.startswith('events:'):
                events = ln[len('events: '):].strip().split(' ')

    if events is None:
        raise ValueError('missing events directive')
    boolTypes = set(['Icov','Iuncov'])
    numEvents = len(events)
    eventTypes = [e in boolTypes for e in events]
    i=0
    for e in events:
        #print e
        if e=="I":
            instIndex= i+2;
        i = i+1

    def readCallNum():
        result = 0
        for elt in inputs:
            while 1:
                ln = getLine(elt)
                if ln is not None and ln.startswith('fl='):
                    pass
                else:
                    #print ln
                    stat = map(int, ln.strip().split(' '))
                    result = stat[instIndex]
                    #print result
                    putback(ln, elt)
                    break
        return result

    def skipLine():
        for elt in inputs:
            ln = getLine(elt)
            break;

    fcount = 0
    fcovd = 0
    finst = 0
    fcovd_inst = 0
    funcs = {}
    fname = ""
    g_instcount = 0
    g_covdinst = 0
    fcall_count=0
    ftime=0
    fquery_time=0
    fqueries=0
    fqueries_valid=0
    fqueries_invalid=0
    fforks = 0
    while 1:
        lns = getLines()
        ln = lns[0]
        if ln is None:
            if int(finst) != 0:
                funcs[fname] = (finst, fcovd_inst, fcall_count, ftime, fquery_time, fqueries, fqueries_valid, fqueries_invalid, fforks)
            break;
        elif ln.startswith('fl') or ln.startswith('cfl') :
            pass
        elif ln.startswith('cfn'):
            pass
        elif ln.startswith('calls'):
            skipLine()    #skip a line after calls
            pass
        elif len(ln.strip()) == 0:
            pass
        elif ln.startswith('fn') :
            #funcs.append(ln[len('fn='):].strip())
            if int(finst) != 0:
                funcs[fname] = (finst, fcovd_inst, fcall_count, ftime, fquery_time, fqueries, fqueries_valid, fqueries_invalid, fforks)
            if int(fcovd_inst) !=0 :
                fcovd += 1
            fname = ln[len('fn='):].strip();
            #print fname
            #print '%s' % funcs[fcount]
            fcount += 1
            finst = 0
            fcovd_inst = 0
            fcall_count = readCallNum()
            ftime = 0
            fforks = 0
            fquery_time=fqueries=fqueries_valid=fqueries_invalid =0
        else :
            #print ln.strip()
            data = [map(int,ln.strip().split(' ')) for ln in lns][0]
            #print data
            if data[2] >0 :
                fcovd_inst += 1
                g_covdinst += 1
                ftime += data[4]
                fquery_time += data[13]
                fqueries += data[10]
                fqueries_valid += data[12]
                fqueries_invalid += data[11]
                fforks += data[3]
            finst += 1
            g_instcount += 1


    #sort funcs
    sortDict={}
    dictCov={}
    dictCalled={}
    dictTime={}
    dictQueryTime={}
    dictQueries={}
    dictForks={}
    allFuncTime = 0
    allFuncNum = 0
    allQueryTime = 0
    coveredFuncNum = 0
    for key in funcs.keys():
        dictCov[key] = funcs[key][1] / funcs[key][0]
        dictCalled[key] = funcs[key][2]
        dictTime[key] = funcs[key][3]
        dictQueryTime[key] = funcs[key][4]
        allQueryTime += funcs[key][4]
        dictQueries[key] = funcs[key][5]
        dictForks[key] = funcs[key][8]
        allFuncTime += funcs[key][3]
        allFuncNum += 1
        if funcs[key][2] != 0:
            coveredFuncNum += 1
            #print key

    if opts.sortID == "callnum":
        sortDict=sorted(dictCalled.items(),key=lambda e:e[1],reverse=True)
    elif opts.sortID == "time":
        sortDict=sorted(dictTime.items(),key=lambda e:e[1],reverse=True)
    elif opts.sortID == "qtime":
        sortDict=sorted(dictQueryTime.items(),key=lambda e:e[1],reverse=True)
    elif opts.sortID == "queries":
        sortDict=sorted(dictQueries.items(),key=lambda e:e[1],reverse=True)
    elif opts.sortID == "cov":
        sortDict=sorted(dictCov.items(),key=lambda e:e[1],reverse=True)
    elif opts.sortID == "forks":
        sortDict=sorted(dictForks.items(),key=lambda e:e[1],reverse=True)
    else:
        sortDict=sorted(dictCov.items(),key=lambda e:e[1],reverse=True)


    print '{:30s} {:10s} {:15s} {:15s} {:15s} {:18s} {:18s} {:16s} {:18s} {:18s} {:16s} {:16s} '.format('FUNC-NAME', 'INST-NUM',
            'COVD_INST', 'Coverage', 'CalledNum', 'TimeUse', 'TimeUse/Call', 'forks', 'QueryTime', 'Queries', 'QueriesValid', 'QueriesInvalid')
    print "-------------------------"
    for item in sortDict:
        #print "%-50s %d" %(item[0], item[1])
        inst=funcs[item[0]][0]
        covd=funcs[item[0]][1]
        callNum = funcs[item[0]][2]
        allTime= funcs[item[0]][3] / 1000000
        TimePerCall = 0
        if callNum != 0:
            TimePerCall = allTime / callNum
        covge=(covd)/(inst)
        querytime = funcs[item[0]][4] / 1000000
        queries = funcs[item[0]][5]
        qvs = funcs[item[0]][6]
        qivs = funcs[item[0]][7]
        fks = funcs[item[0]][8]
        print '{:30s} {:5d} {:10d} {:18f} {:18d} {:18f} {:18f} {:16d} {:18f} {:18d} {:18d} {:18d}'.format(item[0],
                inst, covd, covge, callNum, allTime, TimePerCall, fks, querytime, queries, qvs, qivs)

    print "\n-------------------------\n"
    print "func num = %d, covd func = %d, func coverage = %f" %(allFuncNum, coveredFuncNum, coveredFuncNum/allFuncNum)
    #print "function coverage = %f \n" %(coveredFuncNum / allFuncNum)
    print "inst num = %d covd num = %d, inst coverage=%f" % (g_instcount, g_covdinst, g_covdinst/g_instcount)
    print "used time = %fs, query time= %fs, " %( allFuncTime / 1000000, allQueryTime/1000000  )
    #print "used time = %fs, query time= %fs, ratio=%f" %( allFuncTime / 1000000, allQueryTime/1000000, allQueryTime/allFuncTime )
    print "\n-------------------------\n"

        #print funcs
#    print '{:30s} {:10s} {:15s} {:15s}'.format('FUNC-NAME', 'INST-NUM', 'COVD_INST', 'Coverage', 'CalledNum')
    #print "-------------------------"
    #for key in funcs.keys():
        #inst=funcs[key][0]
        #covd=funcs[key][1]
        #callNum = funcs[key][2]
        #covge=(covd)/(inst)
        #print '{:30s} {:5d} {:10d} {:18f} {:18d}'.format(key, inst, covd, covge, callNum)

    #print "\n\n-------summary----------"
    #print "funcs num = %d covd num = %d, func coverage=%f" % (fcount, fcovd, fcovd/fcount)
    #print "inst num = %d covd num = %d, inst coverage=%f" % (g_instcount, g_covdinst, g_covdinst/g_instcount)
    #print "-------------------------"



def getSummary(input):
    inputs = [[None,iter(open(input))]]
    def getLine(elt):
        la,i = elt
        if la is None:
            try:
                ln = i.next()
            except StopIteration:
                ln = None
            except:
                raise ValueError("unexpected IO error")
            return ln
        else:
            elt[0] = None
            return la
    def getLines():
        return map(getLine,inputs)
    def putback(ln,elt):
        assert elt[0] is None
        elt[0] = ln
        
    events = None
    
    # read header (up to ob=)
    while 1:
        lns = getLines()
        ln = lns[0]
        if ln.startswith('ob='):
            break
        else:
            if ln.startswith('positions:'):
                if ln!='positions: instr line\n':
                    raise ValueError("unexpected 'positions' directive")
            elif ln.startswith('events:'):
                events = ln[len('events: '):].strip().split(' ')

    if events is None:
        raise ValueError('missing events directive')
    boolTypes = set(['Icov','Iuncov'])
    numEvents = len(events)
    eventTypes = [e in boolTypes for e in events]

    def readCalls():
        results = {}
        for elt in inputs:
            print elt
            while 1:
                ln = getLine(elt)
                print "readcalls--%s" % ln
                if ln is not None and (ln.startswith('cfl=') or ln.startswith('cfn=')):
                    if ln.startswith('cfl='):
                        cfl = ln
                        cfn = getLine(elt)
                        if not cfn.startswith('cfn='):
                            raise ValueError("unexpected cfl directive without function")
                    else:
                        cfl = None
                        cfn = ln
                    target = getLine(elt)
                    if not target.startswith('calls='):
                        raise ValueError("unexpected cfn directive with calls")
                    stat = map(int,getLine(elt).strip().split(' '))
                    key = target
                    #print "key=%s" % key
                    #print [cfl,cfn,target,stat]
                    existing = results.get(target)
                    if existing is None:
                        results[key] = [cfl,cfn,target,stat]
                    else:
                        if existing[0]!=cfl or existing[1]!=cfn:
                            raise ValueError("multiple call descriptions for a single target")
                        existing[3] = mergeStats([existing[3],stat])
                else:
                    putback(ln, elt)
                    break
        return results

    summed = [0]*len(events)
    
    # read statistics
    while 1:
        lns = getLines()
        ln = lns[0]
        if ln is None:
            break
        elif ln.startswith('fn') or ln.startswith('fl'):
            pass
        elif ln.strip():
            # an actual statistic
            data = [map(int,ln.strip().split(' ')) for ln in lns][0]
            summed = map(lambda a,b: a+b, data[2:], summed)

            # read any associated calls
            #print ln
            for cfl,cfn,calls,stat in readCalls().values():
                pass

    return events,summed
    
def main(args):
    # inherit from the OptionParser class and override format_epilog
    # in order to get newlines in the 'epilog' text
    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    op = MyParser(usage="usage: %prog [options] run.istat",
                  epilog="""\
LEGEND
------
prog run.istat
parse the run.istat and print out the result, include insts number of function,
covered insts number, coverage , time used .
and the printing infomation also could be sorted by coverage or time used
\n""")


    op.add_option('-s','--sort-by', dest='sortID', help='sorted by it');
    opts,args = op.parse_args()

    total = {}
    for i in args:
        getFuncCov(i, opts)

if __name__=='__main__':
    main(sys.argv)
