set grid x y
set xlabel "Heure"
set ylabel "Pourcentage des validations quotidiennes"

oneday = strptime("%Y-%m-%d", "2000-01-02") - strptime("%Y-%m-%d", "2000-01-01")

set xdata time
set timefmt "%Y-%m-%d %H:%M"
set format x "%H:%M"
set format y "%.2f%%"
set xtic rotate by -45 scale 0 oneday/24

set xrange ["2000-01-02 00:00":"2000-01-03 00:00"]
set yrange [0:0.16]

set linetype 1 linecolor rgb '#40d040' pointsize .1

plot filename using 1:($3*100) with points title 'Répartition moyenne des validations quotidiennes',\
     '' using 1:($3*oneday/24/60*100) smooth kdensity bandwidth oneday/24/3 title 'Densité de probabilité de validations par minute'
