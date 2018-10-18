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

    op = MyParser(usage="usage: %prog -f run.bbcalls-1 -g run.bbcalls-2 ",
                  epilog="""\
LEGEND
------
prog -f run.bbcalls-1 -g run.bbcalls-2  
compare two run.bbcalls to see different bbs coverd in each log file.
\n""")

    op.add_option('-f','--fFile', dest='runFile1', help='run.bbcalls(run.fcalls) file 1');
    op.add_option('-g','--gFile', dest='runFile2', help='run.bbcalls(run.fcalls) file 2 ');
    #op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    runFile1 = open(opts.runFile1,'r')
    sortList=[]

    for ln in runFile1:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            #print data[0]
            #print float(data[0])
            #if float(data[0]) > count:
                #print "%ss touched %s funcs " % (data[0],len(sortList))
                #count += 5
            if data[1] in sortList:
                #print "repeat bb in list"
                #print data[0]
                continue
            else:
                sortList.append(data[1])
                #print data[0]

    runFile1.close()

    listLen1 = len(sortList)
    runFile2 = open(opts.runFile2, 'r')
    SameItems = 0
    sortList2=[]
    for ln in runFile2:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            if len(data) !=2:
                #print "error in :" 
                #print ln
                continue
            if data[1] in sortList2:
                continue
            else:
                sortList2.append(data[1])

            if data[1] in sortList:
                sortList.remove(data[1])
                SameItems = SameItems+1


    runFile2.close()


    listLen2 = len(sortList2)
    print "results:--------"
    print "%d items in %s " % (listLen1, opts.runFile1)
    print "%d items in %s " % (len(sortList2), opts.runFile2)
    print "%d same items, %f based runfile1" % (SameItems, float(SameItems)/float(listLen1))
    print "%d(%f) different with runfile1" % (listLen1-SameItems, float(listLen1-SameItems)/float(listLen1))
    print "%d(%f) different with runfile2" % (listLen2-SameItems, float(listLen2-SameItems)/float(listLen2))
    print "----end\n"




if __name__ == '__main__':
    main(sys.argv)
