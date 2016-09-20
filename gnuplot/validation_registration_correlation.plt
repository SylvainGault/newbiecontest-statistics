set grid x y
set xlabel "Nombre de validations par jour"
set ylabel "Nombre d'inscriptions par jour"

set xrange [0:800]
set yrange [0:50]

set linetype 1 linecolor rgb '#40d040' pointsize .1

plot filename using 2:3 with points title "Nombre d'inscriptions/validations pendant une journée"
