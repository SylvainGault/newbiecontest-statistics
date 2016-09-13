set xlabel 'Année-Mois'
set ylabel 'Nombre de validations'

onemonth = (strptime("%Y", "2004-01") - strptime("%Y", "2000")) / (4 * 12)

set style data boxes
set boxwidth onemonth/2
set xtic rotate by -45 scale 0 onemonth * 6

set yrange [0:]

set xdata time
set timefmt "%Y-%m"
set format x "%Y-%m"

# This makes sharper border with PNG format
set linetype 1 linewidth 1

plot filename using 1:2 title 'Nombre de validations par mois'
