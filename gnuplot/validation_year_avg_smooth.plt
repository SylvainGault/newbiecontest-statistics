set grid x y
set xlabel "Jour de l'année"
set ylabel "Pourcentage de validations annuelles"

oneyear = (strptime("%Y", "2004") - strptime("%Y", "2000")) / 4

set xdata time
set timefmt "%Y-%m-%d"
set format x "%B"
set format y "%.2f%%"
set xtic rotate by -45 scale 0 oneyear/12

set xrange ["2000-01-01":"2000-12-31"]
set yrange [0:0.5]

set linetype 1 linecolor rgb '#40d040' pointsize .1

plot filename using 1:($2*100) with points title 'Répartition moyenne des validations annuelles',\
     '' using 1:($2*oneyear/365*100) smooth kdensity bandwidth oneyear/24 title 'Densité de probabilité de validations annuelles'
