#!/bin/bash
#Filename: pbse-test.sh
#Last modified: 2016-11-11 18:31
# Author: Qixue Xiao <xiaoqixue_1@163.com>
#Description: 

PBSE=/home/xqx/pbse_build/klee/Release+Asserts/bin/klee
GNUPLOT=/usr/bin/gnuplot
TESTDIR=/home/xqx/test
TARGET=$TESTDIR/get_sign/get_sign.o
LIBPNG=/mnt/kleedata/libpng-test/llvm-libpng/libpng-1.2.56/libpng.bca
LTARGET=/mnt/kleedata/libpng-test/llvm-libpng/libpng-1.2.56/pngtest-linked.bc
TESTFILE=""
SYMEXE=1

SEARCHER=""
TIMEOUT=3600
CURDIR=`pwd`
OUTPUTDIR="out"
SANDBOX=/home/xqx/data/xqx/mount/experiment/klee29-test/sandbox.tgz
ENVSH=/home/xqx/data/xqx/mount/experiment/klee29-test/testing-env.sh
WEBDIR=/tmp/
WEBURL="http://166.111.131.12:13380/temp/"
DSTMAIL="xiaoqixue_1@163.com"
MAILMSG="no-msg"

STARTTIME=`date +%Y%m%d%H%M`
ENDTIME=""

#--track-instruction-time \

BASEARGS="-libc=uclibc --posix-runtime   --dump-states-on-halt=false \
    --emit-all-errors --only-output-states-covering-new --output-source=true \
    --max-solver-time=20 \
    --use-forked-solver   \
    --simplify-sym-indices   \
    --switch-type=internal     \
    --disable-inlining  --optimize    \
    --max-sym-array-size=4096   \
    --allow-external-sym-calls \
    --log-func-call=true   \
    --log-func-interval=10  \
    --output-func-id=true"


OUTPUTARGS=""


function usage() {
    
    echo "------klee test usage byxqx------"
    echo ${BASH_SOURCE[0]}
    echo "curDir="$CURDIR
    echo "-u using a env.bash to set klee and target(must before -r)"
    echo "-s searcher"
    echo "-t max watch time"
    echo "-n sym-file size"
    echo "-r linked:run-linked-bc, link:link-llvm-lib"
    echo "-e run in sandbox and testing-env"
    echo "-c(must before any klee opt, ie. -r) run concrete, with (testfile options) at the end"
    echo "-a automatic notify to dest email"
    echo "-f (1:2) dump func trace"
    echo "-l bound , open --loop-bound"
    echo "-m msg, a msg sum send to mail format: \"a-b-c\" "
    echo "-k k in kmeans"

    echo ""

} 

function setConexec() {
    BASEARGS=" -libc=uclibc --posix-runtime \
        --allow-external-sym-calls \
        --switch-type=internal   \
        --phase-test        \
        --log-func-call=true   \
        --log-func-inst-interval=0xff  \
        --output-func-id=true"

    OUTPUTDIR+="-con"
    KLEEARGS=$BASEARGS
    SYMEXE=0
}


function runklee() {
    $PBSE $@ > ${OUTPUTDIR}-log.txt 2>&1
}

function genResult() {
    SRCBC=$CURDIR/$OUTPUTDIR/src-bc.txt
    RUNBBCALLS=$CURDIR/$OUTPUTDIR/run.bbcalls
    RESDIR=$WEBDIR/$OUTPUTDIR
    zcov kleecov $SRCBC $RUNBBCALLS  $RESDIR
}

function sendMail() {
    ENDTIME=`date +%Y%m%d%H%M`
    MAILTITLE="klee-report:$OUTPUTDIR($MAILMSG)"
    MAILCONTENT="$WEBURL/$OUTPUTDIR/index.html"
    TMPFILE=/tmp/mail-$ENDTIME
    cat $CURDIR/$OUTPUTDIR/info > $TMPFILE
    echo "($STARTTIME--$ENDTIME)" >> $TMPFILE
    echo $MAILCONTENT >> $TMPFILE
    cat $TMPFILE | mutt -s $MAILTITLE $DSTMAIL
    #echo $MAILCONTENT | mutt -s $MAILTITLE $DSTMAIL
    rm $TMPFILE
}

function parseEnv {
    cd /tmp/
    tar xvf $SANDBOX 
    cp $ENVSH /tmp/
    env -i /bin/bash -c '(source testing-env.sh; env >/tmp/test.env)'
    cd -

    EnvArgs=" --environ=/tmp/test.env --run-in=/tmp/sandbox "
    KLEEARGS+=$EnvArgs
}

function parseSearcher() {

    case $1 in 
        "dfs")
            SEARCHER=$1
            ;;
        "bfs")
            SEARCHER=$1
            ;;
        "rp")
            SEARCHER="random-path";
            ;;
        "rs")
            SEARCHER="random-state";
            ;;
        "covnew")
            SEARCHER="nurs:covnew"
            ;;
        "default")
            echo "[runtest] searcher using default"
            return
            ;;
    esac
    SearchArgs=" --search=$SEARCHER "
    OUTPUTDIR+="-$1"
    KLEEARGS+=$SearchArgs
    echo "[runtest] searcher using $SEARCHER"

}

function parseMaxTime() {

    TIME=`echo $1 |awk -Fh '{print $1}' `
    case $1 in
        "1h")
            TIMEOUT=3600
            ;;
        "10h")
            TIMEOUT=36000
            ;;
        "24h")
            TIMEOUT=86400
            ;;
        "48h")
            TIMEOUT=$((48*3600))
            ;;
        *)
            TIMEOUT=$(($TIME*3600))
            ;;
    esac

    WatchArgs=" --watchdog --max-time=$TIMEOUT "
    OUTPUTDIR+="-$1"
    KLEEARGS+=$WatchArgs
    echo "[runtest] watch time is $TIMEOUT s"
}

function parseLinkOpt() {
    
    case $1 in
        "linked")
            KLEEARGS+=" --run-linked-bc "
            TARGET=$LTARGET
            echo "[runtest] run linked bc -- $TARGET"
            ;;
        "link")
            KLEEARGS+=" --link-llvm-lib=$LIBPNG "
            echo "[runtest] linking lib -- $LIBPNG"
            ;;
    esac

}
function mainrun() {

    if [ $# == 0 ]
    then
        usage
        return
    fi


    NOTIFY=0
    KLEEARGS=$BASEARGS
    while getopts "s:t:n:r:u:f:l:m:k:peach" arg  
    do
        case $arg in
            s)
                parseSearcher $OPTARG
                ;;
            t)
                parseMaxTime $OPTARG
                ;;
            n)
                SYMNUM=$OPTARG
                OUTPUTDIR+="-$OPTARG"
                ;;
            r)
                parseLinkOpt $OPTARG
                ;;
            e) 
                parseEnv 
                ;;
            u) 
                source $OPTARG
                ;;
            c)
                setConexec 
                ;;
            a)
                NOTIFY=1
                ;;
            f)
                KLEEARGS+=" --dump-func-trace=$OPTARG "
                ;;
            l)
                KLEEARGS+=" --loop-bound=$OPTARG "
                OUTPUTDIR+="-lb$OPTARG"
                ;;
            m)
                MAILMSG=$OPTARG
                echo "msg: "$MAILMSG
                ;;
            k)
                KLEEARGS+=" --kmeans-k=$OPTARG "
                OUTPUTDIR+="-k$OPTARG"
                ;;
            p) 
                shift $(($OPTIND - 1))
                genPhase $@
                return
                ;;
            h)
                usage
                ;;
            ?) 
                #echo "wrong args" $OPTIND
                #usage
                #return
                ;;
        esac

    done

    #rm -rf $OUTPUTDIR
    KLEEARGS+=" --output-dir=$CURDIR/$OUTPUTDIR "

    if [ $SYMEXE == 0 ]
    then
        #concrete exec
        shift $(($OPTIND - 1))
        #echo $@
        TESTFILE=$1
        shift 1
        KLEEARGS+=" $TARGET $@ $TESTFILE"
        #echo $KLEEARGS

        runklee $KLEEARGS

    else
        EXARGS=" --sym-args 2 4 4 --sym-files 2 $SYMNUM "
        KLEEARGS+="$TARGET $EXARGS"
        runklee $KLEEARGS
    fi

    if [ $NOTIFY == 1 ]
    then 
        genResult
        sendMail
    fi

}

function genPhase() {

    # $1: run.bbcalls  $2: phaseinfo
    if [ $# != 2 ]
    then
        usage
        return
    fi

    PHASEFILE="/tmp/phase-tmp.txt"
    sed  -i "/^#/d" $1 
    awk '!a[$1]++' $1 > /tmp/bbcalls-tmp.txt
    paste /tmp/bbcalls-tmp.txt $2 > $PHASEFILE
    OUTPUTDIR=`dirname $1`
    mkdir -p $OUTPUTDIR/phase-$STARTTIME 
    cd $OUTPUTDIR/phase-$STARTTIME 
    K=` awk -F" " '{if(NF==6) printf $6"\n"}' $PHASEFILE |sort -u |wc -l`
    awk '{printf "%-10s %-3s\n", $1, $6 > $6".dat" }' $PHASEFILE
    
$GNUPLOT << EOF  
    reset
    set output "phase.pdf"
    set term pdfcairo font 'times.ttf, 8'
    set xlabel "time(s)"
    set ylabel "bbs"
    set title  "phase represent"
    set yrange [-100:100]
    set ytics -100,100,100
    unset colorbox
    file(n) = sprintf("%d.dat",n);

    plot  for [n=1:$K] for [m=1:5] file(n) u 1:(\$2*5+m):2 w points palette pointtype 7   pointsize 0.1 notitle
    quit
EOF
    

}


mainrun $@
