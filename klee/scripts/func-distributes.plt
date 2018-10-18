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
set ylabel "funcs"
set title  "functions distribution with time"

#set xrange [1:109]
#set xtics 1,10,109

plot "XINPUTX" using 1:2 with points pointtype 7 pointsize 0.01 title "distribution"


#plot ["31-May-04":"11-Jun-04"] 'ibm.dat' using 1:2 with linespoints title "start",  'ibm.dat' using 1:3 with linespoints title "end"


