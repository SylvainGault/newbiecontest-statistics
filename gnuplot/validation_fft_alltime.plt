set grid x y
set logscale x

set xlabel "Période (Jours)"
set ylabel ""

set yrange [0:70000]
unset ytics

set label "Une semaine" at 7,55000 center
set label "4 mois" at 122,40000 center
set label "Un an" at 365,65000 center

plot filename using 1:2 with linespoints title "Transformée de Fourier du nombre de validations par jour"
