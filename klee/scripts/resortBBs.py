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

    op = MyParser(usage="usage: %prog -i con.bbcalls  -o output.bbcalls sym.bbcalls ",
                  epilog="""\
LEGEND
------
prog -i con-bbcalls -o output.bbcalls sym.bbcalls
resort the bbcalls by the order of touched, which is gained from the concrete execution(con.bbcalls).
sym.bbcalls would be resort by it. and output.bbcalls will record the new order.
\n""")

    op.add_option('-i','--conFile', dest='conFile', help='run.bbcalls from concrete execution');
    op.add_option('-o','--outFile', dest='outFile', help='run.rebbcalls for output');
    #op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    conFile = open(opts.conFile,'r')
    sortList=[]
    count = 5

    for ln in conFile:
        if '#' in ln :
            continue
        else:
            #print ln.strip()
            data = ln.strip().split('  ')
            #print data[0]
            #print float(data[0])
            #if float(data[0]) > count:
                #print "%ss touched %s funcs " % (data[0],len(sortList))
                #count += 5
            if data[1] in sortList:
                continue
            else:
                sortList += data[1:2]

    print "===================="
    print len(sortList)

    sortDict = {}
    i=1
    for item in sortList:
        sortDict[item] = i
        i += 1


    listLen = len(sortList)
    symFile = open(args[0],'r')
    outFile = open(opts.outFile, 'w')
    for ln in symFile:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            if len(data) !=4:
                print "error in :" 
                print ln
                return
                continue
            if data[1] in sortList:
                pass
            else:
                #print data[1]
                sortDict[data[1]] = len(sortList)
                sortList += data[1:2]
            outstr = data[0]  + "  " + str(sortDict[data[1]])\
                    + "  " + data[2] + "  " + data[3] + "\n"
            outFile.write(outstr)

    symFile.close()
    outFile.close()







if __name__ == '__main__':
    main(sys.argv)
