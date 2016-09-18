set xlabel "Mois"
set ylabel "Nombre d'inscriptions moyen"

onemonth = (strptime("%Y", "2004") - strptime("%Y", "2000")) / (4 * 12)

set style data boxes
set boxwidth onemonth/2
set xtic rotate by -45 scale 0 onemonth

set yrange [0:]

set xdata time
set timefmt "%m"
set format x "%B"

# This makes sharper border with PNG format
set linetype 1 linewidth 1

plot filename using 1:2 title "Nombre moyen d'inscriptions par mois"
