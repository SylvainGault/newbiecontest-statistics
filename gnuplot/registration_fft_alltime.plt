set grid x y
set logscale x

set xlabel "Période (Jours)"
set ylabel ""

set yrange [0:3500]
unset ytics

set label "Une semaine" at 7,3200 center
set label "4 mois" at 122,2200 center
set label "Un an" at 365,3100 center

plot filename using 1:2 with linespoints title "Transformée de Fourier du nombre d'inscriptions par jour"
