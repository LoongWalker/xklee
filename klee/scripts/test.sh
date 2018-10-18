#!/bin/bash
#Filename: test.sh
#Last modified: 2015-12-30 20:06
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: 

SCRIPTDIR=/home/xqx/data/xqx/projects/xklee-test/klee/scripts
COVINCFILE=covinc.pdf
DATFILE=istat.dat
DATA=aaa

#sed -e "s/XINPUTX/${DATA}/g" ./cov-template.plt
sed -e "s/XINPUTX/${DATFILE}/g" -e "s/XOUTPUTX/${COVINCFILE}/g" $SCRIPTDIR/cov-template.plt
