#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Filename: resortBBs.py
#Last modified: 2016-03-05 14:11
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: 

import sys, os

def main(args) :
    from optparse import OptionParser
    #copy from klee-stats
    # inherit from the OptionParser class and override format_epilog
    # in order to get newlines in the 'epilog' text
    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    op = MyParser(usage="usage: %prog -f id.fbbs -o run.fbbcalls run.bbcalls",
                  epilog="""\
LEGEND
------
prog -f id.fbbs -o run.fbbcalls run.bbcalls
filter bbs or funcs in run.bbcalls(run.fcalls), and the focused bbcalls will be dump to run.fbbcalls
\n""")

    op.add_option('-f','--focuseFile', dest='focuseFile', help='id-fbbs.txt dump from the target');
    op.add_option('-o','--outFile', dest='outFile', help='run.fbbcalls which only contain the focused bbs(funcs)');
    #op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    focuseFile = open(opts.focuseFile,'r')
    sortList=[]
    i=0
    count = 5

    for ln in focuseFile:
        if '#' in ln :
            continue
        else:
            #print ln.strip()
            data = ln.strip().split('\t')
            #print data[0]
            #print float(data[0])
            #if float(data[0]) > count:
                #print "%ss touched %s funcs " % (data[0],len(sortList))
                #count += 5
            if data[0] in sortList:
                print "repeat bb in list"
                print data[0]
                continue
            else:
                sortList.append(data[0])
                #print data[0]

                #print sortList
            #i += 1
            #if i == 10:
                #break

    print "===================="
    print len(sortList)
    #print sortList

    listLen = len(sortList)
    inputFile = open(args[0],'r')
    outFile = open(opts.outFile, 'w')
    for ln in inputFile:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            if len(data) !=2:
                #print "error in :" 
                #print ln
                continue
            if data[1] in sortList:
                outFile.write(ln);
            else:
                pass

    inputFile.close()
    outFile.close()







if __name__ == '__main__':
    main(sys.argv)
