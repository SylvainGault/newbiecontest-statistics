set grid x y front
set xlabel "Heure du jour"
set ylabel "Nombre d'inscriptions moyen"

onehour = strptime("%Y-%m-%d %H", "2000-01-01 01") - strptime("%Y-%m-%d %H", "2000-01-01 00")

set style data boxes
set boxwidth onehour
set xtic rotate by -45 scale 0 onehour

set yrange [0:1]

set xdata time
set timefmt "%H:%M"
set format x "%H:%M"

# This makes sharper border with PNG format
set linetype 1 linewidth 1

plot filename using 1:2 title "Nombre moyen d'inscriptions par heure"
