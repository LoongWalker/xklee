#!/bin/bash
#Filename: gen-covinc.sh
#Last modified: 2016-08-31 10:12
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: proc run.bbcalls 
# generate the covinc plot by run.bbcalls

GNUPLOT=/home/xqx/data/xqx/software/gnuplot/gnuplot-4.6.5/src/gnuplot

function usage()  {
echo "proc [inc|pt-inc|dis] run.bbcalls out.pdf"
}

function genCovinc() {

$GNUPLOT << EOF
reset
set output "$2"
set term pdfcairo font 'times.ttf, 8'
set xlabel "time(s)"
set ylabel "cov"
set title  "coverage increasing by time"

plot "$1" using 1:4 pointtype 7 pointsize 0.1  title "covinc"
quit
EOF

}

function pt_genCovinc() {

$GNUPLOT << EOF
reset
set output "$2"
set term pdfcairo font 'times.ttf, 8'
set xlabel "time(s)"
set ylabel "cov"
set title  "coverage increasing by time"

plot "$1" using 5:4 pointtype 7 pointsize 0.1  title "covinc"
quit
EOF

}

function genCovdis() {

YR="*"
if [ "W"$3 != "W" ]
then
    YR=$3
fi

$GNUPLOT << EOF
reset
set output "$2"
set term pdfcairo font 'times.ttf, 8'
set xlabel "time(s)"
set ylabel "cov"
set title  "coverage distribution"
set yrange [0:$YR]

plot "$1" using 1:2 pointtype 7 pointsize 0.1  title "code distribution"
quit
EOF

}

function mainrun() {

    if [ "W"$1 == "Winc" ] 
    then
        genCovinc $2 $3
    fi
    if [ "W"$1 == "Wpt-inc" ] 
    then
        pt_genCovinc $2 $3
    fi
    if [ "W"$1 == "Wdis" ] 
    then
        genCovdis $2 $3 $4
    fi
    if [ "W"$1 == "W" ] 
    then
        usage
    fi

}


mainrun $@

