#!/bin/bash
#Filename: cov-test.sh
#Last modified: 2016-06-16 09:25
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description:  init: generate the pngs info and a shcmd.txt for concrete execute using kleecon
#  report: $2 : max size expected in pngs; $3: bbnum of the test target; $4: k of kmeans
#         and see the selected pngs in /tmp/pngs-test, /tmp/tmpnewcov.txt shows the coverage info of them


ROOTDIR=/mnt/kleedata/libpng-test/cov-test
PNGSDIR=/mnt/kleedata/libpng-test/pngs
TESTSH=/mnt/kleedata/libpng-test/cov-test/test-1256.sh
COVTEST=/home/xqx/software/cov-test
KMEANS=/home/xqx/data/xqx/projects/xklee-test/klee/scripts/kmeans

if [ "W"$1 == "Winit" ]
then

    rm sizeinfo.txt
    for i in `find $PNGSDIR/ -name "*.png" ` ; do
        #echo $i
        PNGNAME=`basename $i .png`
        echo $TESTSH kleecon 1 $PNGNAME
        FILESIZE=`stat -c %s $i`
        printf '%s \t %s\n' $FILESIZE $PNGNAME >> sizeinfo.txt
    done

fi

if [ "W"$1 == "Wreport" ]
then
    rm /tmp/bbv.txt
    rm /tmp/bbv-order.txt
    MAXSIZE=$2
    COUNT=0
    for i in `find -name bbv.txt` ; do
        FILENAME=`dirname $i`
        PNGNAME=`echo $FILENAME |awk -F'-kleecon' '{print $1}'|awk -F'/' '{print $2}'` 
        PNGNAME=$PNGSDIR/$PNGNAME".png"
        
        FILESIZE=`stat -c %s $PNGNAME`
        if [ $FILESIZE -gt $MAXSIZE ]
        then
            continue
        fi

        #echo $FILESIZE
        #echo $PNGNAME
        COUNT=`expr $COUNT + 1`
        printf '%s \t %s \n' $FILESIZE `basename $PNGNAME` >> /tmp/bbv-order.txt
        cat $i >> /tmp/bbv.txt
    done

    $COVTEST 1 $COUNT $3 only < /tmp/bbv.txt > /tmp/tmpcov.txt
    k=$4
    $KMEANS $k $COUNT $3 < /tmp/bbv.txt 

    cat /tmp/tmpcov.txt |grep "row " > /tmp/row.txt
    cut -d" " -f3 /tmp/row.txt  > /tmp/rowcov.txt
    rm /tmp/row.txt

    paste /tmp/phaseinfo.txt /tmp/rowcov.txt /tmp/bbv-order.txt  > /tmp/covall.txt

    rm -rf /tmp/cov-test
    mkdir -p /tmp/cov-test
    mv /tmp/covall.txt /tmp/cov-test/

    #cd /tmp/cov-test
    awk '{print $0 > "/tmp/cov-test/"$1".dat"}' /tmp/cov-test/covall.txt

    rm /tmp/newbbv.txt
    rm -rf /tmp/pngs-test
    mkdir -p /tmp/pngs-test
    for i in `find /tmp/cov-test/ -name "*.dat"` ; do
        RESFILE=`basename $i .dat`
        cat $i |awk 'BEGIN{max=0; file=""}{if($2>max) {max=$2; file=$4} fi}\
            END{print "max=" max; print "file=" file}' > /tmp/cov-test/$RESFILE.txt
        PNGNAME=`cat /tmp/cov-test/$RESFILE.txt |grep "file" |cut -d"=" -f2`
        cp $PNGSDIR/$PNGNAME /tmp/pngs-test/
        PNGNAME=`basename $PNGNAME .png`

        cat $ROOTDIR/$PNGNAME-kleecon-1/bbv.txt >> /tmp/newbbv.txt

    done

    $COVTEST 1 $k $3  < /tmp/newbbv.txt > /tmp/tmpnewcov.txt

fi



