#!/bin/bash

#needed
sudo apt-get update
sudo apt-get install -y g++ curl dejagnu subversion bison flex bc libcap-dev 
sudo apt-get install -y --no-install-recommends make cmake 
sudo apt-get install -y  zlib1g-dev libncurses-dev python python-dev
sudo apt-get install -y git 

CWD=`pwd`
KLEESRC=/home/xqx/klee-data
KLEEBUILD=/home/xqx/xklee_build

export C_INCLUDE_PATH=/usr/include/x86_64-linux-gnu
export CPLUS_INCLUDE_PATH=/usr/include/x86_64-linux-gnu
#download llvm-gcc and put it to $PATH
if [ ! -d llvm-gcc4.2-2.9-x86_64-linux ]
then
        cp -r $KLEESRC/llvm-gcc4.2-2.9-x86_64-linux ./
fi
cd $(dirname $(find $KLEESRC -type f -name llvm-gcc))
export PATH=$(pwd):${PATH}
cd $CWD

#build llvm-2.9
if [ ! -d llvm-2.9 ]
then
    tar zxvf $KLEESRC/llvm-2.9.tgz
fi
#for gcc >= 4.7
 sed -i '1 i#include <unistd.h>' llvm-2.9/lib/ExecutionEngine/JIT/Intercept.cpp
cd llvm-2.9
./configure --enable-optimized --enable-assertions \
&& make -j `grep -c processor /proc/cpuinfo`
if [ $? != 0 ]
then
        echo "llvm 2.9 --- failed..."
        exit 1
fi
cd $(dirname $(find -type f -name llvm-nm))
export PATH=$(pwd):${PATH}
cd -
cd $CWD

#build stp

## minisat needed by STP 2.1.0
if [ ! -d minisat ]
then
    #cp -r $KLEESRC/minisat .
    mkdir minisat
fi
cd minisat
mkdir build
cd build
cmake $KLEESRC/minisat
make
sudo make install
if [ $? != 0 ]
then
        echo "minisat --- failed..."
        exit 1
fi
cd ../../

if [ ! -d stp-2.1.0 ]
then
    #tar xzfv 2.1.0.tar.gz
    mkdir stp-2.1.0
fi
cd stp-2.1.0
mkdir build
cd build
cmake $KLEESRC/stp-2.1.0
make -j `grep -c processor /proc/cpuinfo`
sudo make install

if [ $? != 0 ]
then
        echo "stp --- failed..."
        exit 1
fi

ulimit -s unlimited

##build klee-uclibc
cd ${CWD}
#git clone --depth 1 --branch klee_0_9_29 https://github.com/klee/klee-uclibc.git
git clone  https://github.com/klee/klee-uclibc.git
cd klee-uclibc/
./configure --make-llvm-lib \
&& make -j `grep -c processor /proc/cpuinfo`
if [ $? != 0 ]
then
        echo "klee-uclibc --- failed..."
        exit 1
fi
cd ../

#build klee
#export C_INCLUDE_PATH=/usr/include/x86_64-linux-gnu
#git clone https://github.com/ccadar/klee.git
#git clone https://github.com/klee/klee.git
mkdir klee
cd ${CWD}/klee
$KLEESRC/klee/configure --with-llvm=${CWD}/llvm-2.9 --with-stp=${CWD}/stp-2.1.0/build  --with-uclibc=${CWD}/klee-uclibc --enable-posix-runtime
# ./configure # --with-llvm=../llvm-2.9 --with-stp=../stp-r940/install --with-uclibc=../klee-uclibc --enable-posix-runtime \
#&&  make ENABLE_OPTIMIZED=1 -j `grep -c processor /proc/cpuinfo`
make #upline cmd may fail
#make ENABLE_OPTIMIZED=0 CXXFLAGS="-g -O0"
if [ $? != 0 ]
then
        echo "klee --- failed..."
        exit 1
fi
cd -

echo "==================="
echo "编译完成，开始测试"
echo "==================="

cd klee
make check
make unittests
cd -
echo "测试结束，请根据上述测试结果判断是否编译成功！"
echo "脚本结束！"
