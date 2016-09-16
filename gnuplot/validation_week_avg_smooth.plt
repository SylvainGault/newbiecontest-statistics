set grid x y
set xlabel "Jour de la semaine"
set ylabel "Pourcentage de validations hebdomadaires"

oneday = strptime("%Y-%m-%d", "2000-01-02") - strptime("%Y-%m-%d", "2000-01-01")

set xdata time
set timefmt "%Y-%m-%d %H:%M"
set format x "%A"
set format y "%.2f%%"
set xtic rotate by -45 scale 0 oneday

set xrange ["2006-12-11 00:00":"2006-12-18 00:00"]
set yrange [0:1.5]

set linetype 1 linecolor rgb '#40d040' pointsize .1

plot filename using 1:($3*100) with points title 'Répartition moyenne des validations hebdomadaires',\
     '' using 1:($3*oneday/24*100) smooth kdensity bandwidth oneday/2.5 title 'Densité de probabilité de validations hebdomadaires'
