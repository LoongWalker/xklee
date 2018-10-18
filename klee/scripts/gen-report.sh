#!/bin/bash
#Filename: gen-report.sh
#Last modified: 2015-12-30 19:48
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: generate report of klee reports
#input is arg1: klee-out dir
# arg2: the dir to output the results
# arg3: [func]: if report the function distribution
# arg4: concrete klee-out dir. for resorting the func or bbs by the concrete order


#SCRIPTDIR=/home/xqx/data/xqx/projects/xklee-test/klee/scripts
SCRIPTDIR=$(dirname "${BASH_SOURCE[0]}")
XCOV=$SCRIPTDIR/xCov.py
GENCG=$SCRIPTDIR/genCallgraph.py
RESORTBBS=$SCRIPTDIR/resortBBs.py
FILTERFOCUSE=$SCRIPTDIR/filterFocuse.py
INPUTDIR=./klee-last
OUTPUTDIR=/tmp/klee-report
DATFILE=istat.dat
COVINCFILE=covinc.pdf
TIMEINCFILE=timeinc.pdf

FUNCFILE=run.fcalls
FUNCDISTFILE=funcdis.pdf

CALLINSTFILE=run.callinsts
CALLINSTDIST=callinstdis.pdf

BBCALLSFILE=run.bbcalls
BBDISTFILE=bbdis.pdf

REBBCALLSFILE=run.rebbcalls
REBBDISTFILE=rebbdis.pdf

REFORKSFILE=run.reforks
REFORKSDISTFILE=reforks.pdf

FBBCALLSFILE=run.fbbcalls
FBBDISTFILE=fbbdis.pdf

REFBBCALLSFILE=run.refbbcalls
REFBBDISTFILE=refbbdis.pdf

if [ $# != 0 ]
then
    INPUTDIR=$1
fi

if [ "W"$2 != "W" ]
then
    OUTPUTDIR=$2
fi
rm -rf $OUTPUTDIR
mkdir $OUTPUTDIR

# first generate the coverage of every function
echo "generate functions coverage report..."
$XCOV -s time $INPUTDIR/run.istats > $OUTPUTDIR/sort-by-time.txt 
$XCOV -s cov $INPUTDIR/run.istats >  $OUTPUTDIR/sort-by-cov.txt 
$XCOV -s forks $INPUTDIR/run.istats >  $OUTPUTDIR/sort-by-forks.txt 

$XCOV -s time $INPUTDIR/run.fistats > $OUTPUTDIR/fsort-by-time.txt 
$XCOV -s cov $INPUTDIR/run.fistats >  $OUTPUTDIR/fsort-by-cov.txt 

#second
echo "generate coverage increasing graph..."
sed  -e '1d' -e 's/(//g' -e 's/)//g' -e 's/,/  /g' $INPUTDIR/run.stats > $DATFILE

sed -e "s/XINPUTX/${DATFILE}/g" -e "s/XOUTPUTX/${COVINCFILE}/g" $SCRIPTDIR/cov-template.plt > $OUTPUTDIR/cov.plt
gnuplot $OUTPUTDIR/cov.plt

sed -e "s/XINPUTX/$DATFILE/g" -e "s/XOUTPUTX/$TIMEINCFILE/g" $SCRIPTDIR/time-template.plt > $OUTPUTDIR/time.plt
gnuplot $OUTPUTDIR/time.plt

mv $COVINCFILE $OUTPUTDIR/
mv $TIMEINCFILE  $OUTPUTDIR/
mv $DATFILE $OUTPUTDIR/


# third , generate callgraphs
echo "generate callgraphs ..."
cp $INPUTDIR/callgraph.dot $OUTPUTDIR/
cp $INPUTDIR/cpgraph.dot $OUTPUTDIR/

$GENCG -i $INPUTDIR/run.istats -o $OUTPUTDIR/marked-callgraph.dot  $INPUTDIR/callgraph.dot > /dev/null


if [ "W"$3 == "Wfunc" ]
then
    sed -e '1d' $INPUTDIR/run.fcalls >  $FUNCFILE
    sed -e "s/XINPUTX/${FUNCFILE}/g" -e "s/XOUTPUTX/${FUNCDISTFILE}/g" $SCRIPTDIR/func-distributes.plt > $OUTPUTDIR/func.plt
    gnuplot $OUTPUTDIR/func.plt
    
    sed -e '1d' $INPUTDIR/run.callinsts >  $CALLINSTFILE
    sed -e "s/XINPUTX/${CALLINSTFILE}/g" -e "s/XOUTPUTX/${CALLINSTDIST}/g" $SCRIPTDIR/callinst-distributes.plt > $OUTPUTDIR/callinst.plt
    gnuplot $OUTPUTDIR/callinst.plt

    sed -e '1d' $INPUTDIR/run.bbcalls >  $BBCALLSFILE
    sed -e "s/XINPUTX/${BBCALLSFILE}/g" -e "s/XOUTPUTX/${BBDISTFILE}/g" $SCRIPTDIR/bb-distributes.plt > $OUTPUTDIR/bb.plt
    gnuplot $OUTPUTDIR/bb.plt

    $FILTERFOCUSE -f $INPUTDIR/id-fbbs.txt -o $INPUTDIR/run.fbbcalls $INPUTDIR/run.bbcalls
    sed -e '1d' $INPUTDIR/run.fbbcalls >  $FBBCALLSFILE
    sed -e "s/XINPUTX/${FBBCALLSFILE}/g" -e "s/XOUTPUTX/${FBBDISTFILE}/g" $SCRIPTDIR/bb-distributes.plt > $OUTPUTDIR/fbb.plt
    gnuplot $OUTPUTDIR/fbb.plt


    if [ "W"$4 != "W" ]
    then
        $RESORTBBS -i $4/run.bbcalls -o $INPUTDIR/run.rebbcalls $INPUTDIR/run.bbcalls
        sed -e '1d' $INPUTDIR/run.rebbcalls >  $REBBCALLSFILE
        sed -e "s/XINPUTX/${REBBCALLSFILE}/g" -e "s/XOUTPUTX/${REBBDISTFILE}/g" $SCRIPTDIR/bb-distributes.plt > $OUTPUTDIR/rebb.plt
        gnuplot $OUTPUTDIR/rebb.plt

        $RESORTBBS -i $4/run.bbcalls -o $INPUTDIR/run.reforks $INPUTDIR/run.forks
        cat $INPUTDIR/run.reforks >  $REFORKSFILE
        sed -e "s/XINPUTX/${REFORKSFILE}/g" -e "s/XOUTPUTX/${REFORKSDISTFILE}/g" $SCRIPTDIR/bb-distributes.plt > $OUTPUTDIR/reforks.plt
        gnuplot $OUTPUTDIR/reforks.plt

        $RESORTBBS -i $4/run.bbcalls -o $INPUTDIR/run.refbbcalls $INPUTDIR/run.fbbcalls
        sed -e '1d' $INPUTDIR/run.refbbcalls >  $REFBBCALLSFILE
        sed -e "s/XINPUTX/${REFBBCALLSFILE}/g" -e "s/XOUTPUTX/${REFBBDISTFILE}/g" $SCRIPTDIR/bb-distributes.plt > $OUTPUTDIR/refbb.plt
        gnuplot $OUTPUTDIR/refbb.plt
    fi

    mv $FUNCFILE $OUTPUTDIR/
    mv $FUNCDISTFILE $OUTPUTDIR/
    mv $CALLINSTFILE $OUTPUTDIR/
    mv $CALLINSTDIST  $OUTPUTDIR/
    mv $BBCALLSFILE $OUTPUTDIR/
    mv $BBDISTFILE  $OUTPUTDIR/
    mv $REBBCALLSFILE $OUTPUTDIR/
    mv $REBBDISTFILE  $OUTPUTDIR/
    mv $FBBCALLSFILE $OUTPUTDIR/
    mv $FBBDISTFILE  $OUTPUTDIR/
    mv $REFBBCALLSFILE $OUTPUTDIR/
    mv $REFBBDISTFILE $OUTPUTDIR/
    mv $REFORKSFILE  $OUTPUTDIR/
    mv $REFORKSDISTFILE $OUTPUTDIR/

fi


echo ""
echo "=================================================="
echo "generate reports ok! please see $OUTPUTDIR"
echo "$COVINCFILE shows the coverage increasing with time "
echo "$TIMEINCFILE shows the time used in execution with time"
echo "marked-callgraph.dot shows the functions called in callgraph"
echo "sort-by-time.txt shows each function coverage and sorted by time used in each function "
echo "=================================================="

