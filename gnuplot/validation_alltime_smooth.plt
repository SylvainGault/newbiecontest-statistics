set grid x y
set xlabel 'Date'
set ylabel 'Nombre de validations'

oneyear = (strptime("%Y", "2004") - strptime("%Y", "2000")) / 4

set xdata time
set timefmt "%Y-%m-%d"
set format x "%Y"
set xtic rotate by -45 scale 0 oneyear

set yrange [0:500]

set linetype 1 linecolor rgb '#40d040' pointsize .1

plot filename using 1:2 with points title 'Nombre de validations ce jour',\
     '' using 1:($2*oneyear/365) smooth kdensity bandwidth oneyear/6 title 'Nombre de validations par jour lissé'
