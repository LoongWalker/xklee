#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Filename: genCallgraph.py
#Last modified: 2015-12-28 10:58
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: 


import sys, os
import re
from collections import defaultdict

#dictNode = {"NODEID" : "FUNCNAME"}
#dictEdge = {"NODEID" : ["NODEID1", "NODEID2"]}
dictNode = {}
covedFuncs = {}
dictEdge = defaultdict(list)

def getFuncCov(input):
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
    print "-------------------------"
    for key in covedFuncs.keys():
        inst=covedFuncs[key][0]
        covd=covedFuncs[key][1]
        covge=(covd)/(inst)
        print '{:30s} {:5d} {:10d} {:18f}'.format(key, inst, covd, covge)

    print "\n\n-------summary----------"
    print "covedFuncs num = %d covd num = %d, func coverage=%f" % (fcount, fcovd, fcovd/fcount)
    print "inst num = %d covd num = %d, inst coverage=%f" % (g_instcount, g_covdinst, g_covdinst/g_instcount)
    print "-------------------------"


def parseFuncs(line, outfile):
    nodeName=line[1:15]
    #print nodeName
    a1 = re.compile('\{(.*?)\}')
    funcName = a1.findall(line)
    #print funcName
    #dictNode[nodeName] = funcName[0]
    dictNode[funcName[0]] = nodeName
    if funcName[0] in covedFuncs :
        if covedFuncs[funcName[0]][1] != 0 :
            str = "\t" + nodeName + "[shape=record, label=\"{" + funcName[0];
            str += "}\", fillcolor=\"#FFAA22\", style=filled];\n"
            outfile.write(str);
        else:
            outfile.write(line)

    else:
        outfile.write(line)




def parseFuncsAdd(line, outfile):
    nodeName=line[1:15]
    #print nodeName
    a1 = re.compile('\{(.*?)\}')
    funcName = a1.findall(line)
    #print funcName
    #dictNode[nodeName] = funcName[0]
    dictNode[funcName[0]] = nodeName
    if funcName[0] in covedFuncs :
        if covedFuncs[funcName[0]][1] != 0 :
            if line.count("fillcolor") ==0 :
                str = "\t" + nodeName + "[shape=record, label=\"{" + funcName[0];
                str += "}\", fillcolor=\"#FF0022\", style=filled];\n"
                outfile.write(str);
            else:
                str = "\t" + nodeName + "[shape=record, label=\"{" + funcName[0];
                str += "}\", fillcolor=\"#FFAAFF\", style=filled];\n"
                outfile.write(str);
        else:
            outfile.write(line)

    else:
        outfile.write(line)


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

    op.add_option('-i','--istat', dest='ifile', help='run.istat in klee-out');
    op.add_option('-o','--out-file', dest='ofile', help='generate new callgraph.dot');
    op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    getFuncCov(opts.ifile)

    f = open(args[0])
    fout = open(opts.ofile,'w')

    for ln in f:
        #print ln.strip("\n")
        if '->' not in ln and 'NODE' in ln and 'label=' in ln:
          #print ln.strip("\n") 
          if opts.addfile:
              parseFuncsAdd(ln,fout)
          else:
              parseFuncs(ln,fout)

        elif '->' in ln :
            nodes = ln.strip().split(' ')
            dictEdge[nodes[0]].append(nodes[2])
            fout.write(ln)
            #print nodes[0]
            #print nodes[2]

        else:
            fout.write(ln)

    #for key in dictNode.keys():
        #print 'key=%s, value=%s' % (key, dictNode[key])
    #for key in dictEdge.keys():
        #print 'key=%s, value=%s' % (key, dictEdge[key])



if __name__ == '__main__':
    main(sys.argv)
