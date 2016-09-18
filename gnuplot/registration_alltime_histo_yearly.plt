set xlabel "Année"
set ylabel "Nombre d'inscriptions"

oneyear = (strptime("%Y", "2004") - strptime("%Y", "2000")) / 4

set style data boxes
set boxwidth oneyear/2
set xtic rotate by -45 scale 0 oneyear

set yrange [0:]

set xdata time
set timefmt "%Y"
set format x "%Y"

# This makes sharper border with PNG format
set linetype 1 linewidth 1

plot filename using 1:2 title "Nombre d'inscriptions par an"
