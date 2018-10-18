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

    op = MyParser(usage="usage: %prog con.bbcalls sym.bbcalls output.bbcalls",
                  epilog="""\
LEGEND
------
prog -a addtime  -o output.bbcalls sym.bbcalls
this prog merge the execution info(sym.bbcalls) to a file(output.bbcalls), and add the specified time

addtime means the time should be added in the sym.bbcalls whose first colomn is show time.
output.bbcalls means the file merge to, it would append to the tail if it exists data
sym.bbcalls means the file merge from.
\n""")

    #op.add_option('-i','--conFile', dest='conFile', help='run.bbcalls from concrete execution');
    op.add_option('-o','--outFile', dest='outFile', help='run.bbcalls merge to');
    op.add_option('-a','--add-time', dest='addtime', type="float", help='add a istat file');
    opts,args = op.parse_args()  

    inFile = open(args[0],'r')
    outFile= open(opts.outFile,'a+')
    sortList=[]
    i=0
    count = 5

    for ln in inFile:
        if '#' in ln :
            continue
        else:
            #print ln.strip()
            data = ln.strip().split('  ')
            #print data[0]
            #print float(data[0])
            newtime = float(data[0]) + opts.addtime
            outstr = str(newtime) + "  " +  str(data[1]) + "\n"
            outFile.write(outstr)



    inFile.close()
    outFile.close()









if __name__ == '__main__':
    main(sys.argv)
