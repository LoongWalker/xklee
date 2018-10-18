reset
set output "XOUTPUTX"
set term pdfcairo font 'times.ttf, 8'
#set xdata time
#set timefmt  "%d-%b-%y"
#set format x "%b %d"

#set style data histogram
#set style histogram clustered gap 1
#set style fill solid 0.4 border

set xlabel "time(s)"
set ylabel "time ratio"
set title  " time used in the execution "

#set xrange [1:109]
#set xtics 1,10,109

#plot "XINPUTX" using 11:($12/($12+$13)) w l title "all", "XINPUTX" using 11:($14/($14+$15)) w l lc 3 title "focused"
plot "XINPUTX" using 11:($16/($11)) w l title "QueryTime", "XINPUTX" using 11:($17/($11)) w l lc 3 title "SolverTime", \
        "XINPUTX" using 11:($19/($11)) w l lc 4 title "ForkTime", "XINPUTX" using 11:($20/($11)) w l lc 5 title "ResolveTime", \
        "XINPUTX" using 11:(($11-$17-$19)/$11) w l lc 7 title "ExecTime";




#plot ["31-May-04":"11-Jun-04"] 'ibm.dat' using 1:2 with linespoints title "start",  'ibm.dat' using 1:3 with linespoints title "end"


