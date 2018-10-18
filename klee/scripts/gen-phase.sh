#!/bin/bash
#Filename: gen-phase.sh
#Last modified: 2016-05-16 15:33
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: arg1: run.rebbcalls  arg2: k of kmeans

if [ $# == 0 ]
then
    echo "prog run.rebbcalls k(kmeans)"
    echo "pleas see newphase.pdf for the info of phase"
    exit
fi

SCRIPTDIR=$(dirname "${BASH_SOURCE[0]}")
GENBBV=$SCRIPTDIR/genBBV.py

TIMESTAMP=$(date +%Y%m%d%H%M)
PHASETMPFILE=/tmp/phase-$TIMESTAMP
TIMETMPFILE=/tmp/utime-$TIMESTAMP
#KMEANS=/home/xqx/data/xqx/projects/kmeans-test/k-means/kmeans
KMEANS=$SCRIPTDIR/kmeans
PHASEINFOFILE=/tmp/phase-$TIMESTAMP-info.txt
TIMEPHASEFILE=/tmp/time-$TIMESTAMP-phase.txt
GNUPLOT=/home/xqx/data/xqx/software/gnuplot/gnuplot-4.6.5/src/gnuplot

PHASESDIR=/tmp/ps-$TIMESTAMP

$GENBBV -i $1 -o $PHASETMPFILE -t $TIMETMPFILE

cut -d" " -f3 $TIMETMPFILE > /tmp/tmpcov.txt
cp $PHASETMPFILE /tmp/tmpphase.txt
#COVNUM=`cat /tmp/tmpcov.txt |wc -l`
#awk -v n=$COVNUM '{print NR/n " " sqrt($1)}' /tmp/tmpcov.txt > /tmp/tmpcov1.txt
awk '{print sqrt($1)*20}' /tmp/tmpcov.txt > /tmp/tmpcov1.txt
mv /tmp/tmpcov1.txt /tmp/tmpcov.txt
paste /tmp/tmpcov.txt /tmp/tmpphase.txt > $PHASETMPFILE
#rm /tmp/tmpcov.txt /tmp/tmpphase.txt

K=$2
VNUM=`head -n1 $PHASETMPFILE | awk '{print NF}'`
NNUM=`cat $TIMETMPFILE |wc -l`

echo $K $NNUM $VNUM

$KMEANS $K $NNUM $VNUM $PHASEINFOFILE < $PHASETMPFILE

paste $TIMETMPFILE $PHASEINFOFILE > $TIMEPHASEFILE

mkdir -p $PHASESDIR-$K-$NNUM-$VNUM

cd $PHASESDIR-$K-$NNUM-$VNUM
awk '{printf "%-10s %-3s\n", $1, $3 > $3".dat" }' $TIMEPHASEFILE

$GNUPLOT << EOF
    reset
    set output "newphase.pdf"
    set term pdfcairo font 'times.ttf, 8'
set xlabel "time(s)"
set ylabel "bbs"
set title  "new phase represent"
set yrange [-100:100]
set ytics -100,100,100
unset colorbox
file(n) = sprintf("%d.dat",n);

plot  for [n=1:$K] for [m=1:5] file(n) u 1:(\$2*5+m):2 w points palette pointtype 7   pointsize 0.1 notitle
quit
EOF
#plot  for [n=1:$K] for [m=1:5] file(n) u 1:(\$2*5+m):2 w points palette pointtype 7   pointsize 0.1 notitle

cd -






