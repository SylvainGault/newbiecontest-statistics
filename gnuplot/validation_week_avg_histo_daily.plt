set xlabel 'Jour de la semaine'
set ylabel 'Nombre de validations moyen'

oneday = strptime("%Y-%m-%d", "2000-01-02") - strptime("%Y-%m-%d", "2000-01-01")

set style data boxes
set boxwidth oneday/2
set xtic rotate by -45 scale 0 oneday

set yrange [0:260]

set xdata time
set timefmt "%Y-%m-%d"
set format x "%A"

# This makes sharper border with PNG format
set linetype 1 linewidth 1

plot filename using 1:2 title 'Nombre moyen de validations par jour de la semaine'
