xklee
==============

xklee perfroms partial symbolic execution with concolic file system environment model.


1. install

xklee could be installed as the same as klee, please see https://klee.github.io/.

or

you could use the script to build xklee. (AutoBuildKlee-docker.sh)

or

your could download from docker hub, ( https://hub.docker.com/u/xqx12/  )


2. usage

-xqx-sym-file concrete-file off len 2

example:

-xqx-sym-file /tmp/basn/png-format/basn0g02.png 0 8 2

it specifies the 0-8 bytes in /tmp/basn/png-format/basn0g02.png to be symbolic data, and others are concrete data.





