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

    op = MyParser(usage="usage: %prog -i run.rebbcalls -o bbvs.file",
                  epilog="""\
LEGEND
------
prog -i run.rebbcalls -o bbvs file
generate bbvs from run.rebbcalls
\n""")

    op.add_option('-i','--inputFile', dest='inFile', help='run.rebbcalls , bb calls when by execution');
    op.add_option('-o','--outFile', dest='outFile', help='format to a BBV from the inputFile');
    op.add_option('-t','--outTimeFile', dest='outTimeFile', help='generate time file related to  BBV outFile');
    #op.add_option('-a','--add-file', dest='addfile', action='store_true', help='add a istat file');
    opts,args = op.parse_args()

    inputFile = open(opts.inFile,'r')
    maxNum=0
    for ln in inputFile:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            #if len(data) !=2:
                #continue
            if int(data[1]) > maxNum:
                #print data[1]
                maxNum= int(data[1])
            else:
                pass

    print("MaxNUM is %d " % (maxNum))

    inputFile.seek(0, 0)
    outFile = open(opts.outFile, 'w')
    outTimeFile = open(opts.outTimeFile, 'w')
    lastIndex=0.0
    lastCov=0
    tmpList=[0 for n in range(0, maxNum+1)]
    tmpList2=[]
    for ln in inputFile:
        if '#' in ln :
            continue
        else:
            data = ln.strip().split('  ')
            if len(data) != 4 :
                print "error in :" 
                print ln
                exit
                continue
            if lastIndex == 0.0:
                lastIndex = float(data[0])
                lastCov = data[3]
                tmpList[int(data[1])] += int(data[2])
                tmpList2.append(int(data[1]))

            elif float(data[0]) != lastIndex:
                outTimeFile.write(str(lastIndex))
                outTimeFile.write("  ")
                outTimeFile.write(lastCov)
                outTimeFile.write("\n")
                sumCalls=0
                for i in range(1,maxNum+1):
                    sumCalls += int(tmpList[i]);
                for i in range(1,maxNum+1):
                    outFile.write(str(float(tmpList[i]) / float(sumCalls)));
                    #print("%d: %f, %s" % (i,tmpList[i], str(float(tmpList[i]/float(sumCalls))))) 
                    outFile.write(" ");
                    #if i in tmpList:
                        ##print "1 ",
                        #outFile.write("1 ")
                    #else:
                        #outFile.write("0 ")
                        ##print "0 ",
                #print ""
                outFile.write("\n")
                lastIndex=float(data[0])
                lastCov = data[3]
                tmpList=[0 for n in range(0, maxNum+1)]
                tmpList2=[]
                tmpList[int(data[1])] += int(data[2])
                tmpList2.append(int(data[1]))

            else:
                tmpList[int(data[1])] += int(data[2])
                tmpList2.append(int(data[1]))
                pass

    if len(tmpList2) > 0 :
        outTimeFile.write(data[0])
        outTimeFile.write("  ")
        outTimeFile.write(data[3])
        outTimeFile.write("\n")
        for i in range(1,maxNum+1):
            sumCalls += int(tmpList[i]);
        for i in range(1,maxNum+1):
            outFile.write(str(float(tmpList[i]) / float(sumCalls)));
            outFile.write(" ");
        #for i in range(1,maxNum+1):
            #outFile.write(str(tmpList[i]));
            #outFile.write(" ");
        outFile.write("\n")

    inputFile.close()
    outFile.close()







if __name__ == '__main__':
    main(sys.argv)
