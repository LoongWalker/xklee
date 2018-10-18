#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Filename: compCov.py
#Last modified: 2016-03-01 07:41
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: 

from __future__ import division
import sys, os
import re
from collections import defaultdict

#dictNode = {"NODEID" : "FUNCNAME"}
#dictEdge = {"NODEID" : ["NODEID1", "NODEID2"]}
dictNode = {}
dictEdge = defaultdict(list)

def getFuncCov(input):
    covedFuncs = {}
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

    fcount = 0
    fcovd = 0
    finst = 0
    fcovd_inst = 0
    fname = ""
    g_instcount = 0
    g_covdinst = 0
    while 1:
        lns = getLines()
        ln = lns[0]
        if ln is None:
            if int(finst) != 0:
                covedFuncs[fname] = (finst, fcovd_inst)
            break;
        elif ln.startswith('fl') or ln.startswith('cfl') :
            pass
        elif ln.startswith('cfn') or ln.startswith('calls'):
            pass
        elif len(ln.strip()) == 0:
            pass
        elif ln.startswith('fn') :
            #covedFuncs.append(ln[len('fn='):].strip())
            if int(finst) != 0:
                covedFuncs[fname] = (finst, fcovd_inst)
            if int(fcovd_inst) !=0 :
                fcovd += 1
            fname = ln[len('fn='):].strip();
            #print fname
            #print '%s' % covedFuncs[fcount]
            fcount += 1
            finst = 0
            fcovd_inst = 0
        else :
            #print ln.strip()
            data = [map(int,ln.strip().split(' ')) for ln in lns][0]
            #print data
            if data[2] >0 :
                fcovd_inst += 1
                g_covdinst += 1
            finst += 1
            g_instcount += 1

    #print covedFuncs
#    print '{:30s} {:10s} {:15s} {:15s}'.format('FUNC-NAME', 'INST-NUM', 'COVD_INST', 'Coverage')
    #covedFuncs1 = covedFuncs;
    #print "-------------------------"
    #for key in covedFuncs.keys():
        #inst=covedFuncs[key][0]
        #covd=covedFuncs[key][1]
        #covge=(covd)/(inst)
        #print '{:30s} {:5d} {:10d} {:18f}'.format(key, inst, covd, covge)

    #print "\n\n-------summary----------"
    #print "covedFuncs num = %d covd num = %d, func coverage=%f" % (fcount, fcovd, fcovd/fcount)
    #print "inst num = %d covd num = %d, inst coverage=%f" % (g_instcount, g_covdinst, g_covdinst/g_instcount)
    #print "-------------------------"

    return covedFuncs;

def printCovDisc(covDisc):
    fcount = 0
    fcovd = 0
    g_instcount = 0
    g_covdinst = 0
    print "-------------------------"
    for key in covDisc.keys():
        inst=covDisc[key][0]
        covd=covDisc[key][1]
        covge=(covd)/(inst)
        #print '{:30s} {:5d} {:10d} {:18f}'.format(key, inst, covd, covge)
        fcount += 1;
        if covd != 0:
            fcovd += 1;
        g_instcount += inst
        g_covdinst += covd

    print "\n\n-------summary----------"
    print "covedFuncs num = %d covd num = %d, func coverage=%f" % (fcount, fcovd, fcovd/fcount)
    print "inst num = %d covd num = %d, inst coverage=%f" % (g_instcount, g_covdinst, g_covdinst/g_instcount)
    print "-------------------------"


def discardUcovedFunc(covDisc):
    result = set()
    for key in covDisc.keys():
        covd=covDisc[key][1]
        if covd != 0:
            result.add(key)

    return result



def main(args) :
    from optparse import OptionParser
    #copy from klee-stats
    # inherit from the OptionParser class and override format_epilog
    # in order to get newlines in the 'epilog' text
    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    op = MyParser(usage="usage: %prog [options] callgraph.dot",
                  epilog="""\
LEGEND
------
prog -i run.istat -o output.dot callgraph.dot
parse callgraph.dot and run.istat, generate a new callgraph which marking the
covered functions with the different color.
\n""")

    op.add_option('-f','--file1', dest='file1', help='run.istat in klee-out');
    op.add_option('-g','--file2', dest='file2', help='run.istat in klee-out');
    #op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    covedFuncs1 = {}
    covedFuncs2 = {}

    covedFuncs1 = getFuncCov(opts.file1)
    printCovDisc(covedFuncs1)
    covedFuncs2 = getFuncCov(opts.file2)
    printCovDisc(covedFuncs2)

    covedFuncSet1 = set()
    covedFuncSet1 = discardUcovedFunc(covedFuncs1)
    num1 = len(covedFuncSet1)
    covedFuncSet2 = set()
    covedFuncSet2 = discardUcovedFunc(covedFuncs2)
    num2 = len(covedFuncSet2)
    
    num21 = len(covedFuncSet2 - covedFuncSet1)
    num12 =  len(covedFuncSet1 - covedFuncSet2)

    print "set1 coved funcs = %d, set2 coved funcs = %d" % (num1, num2);
    print "set1 coved but not set2 = %d, (%f)" % (num12, num12/num1) 
    print "set2 coved but not set1 = %d, (%f)" % (num21, num21/num2) 

    #f = open(args[0])
    #fout = open(opts.file1,'w')
    

if __name__ == '__main__':
    main(sys.argv)
