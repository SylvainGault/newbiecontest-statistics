set terminal pngcairo font ",10" size 800,600
set key box right opaque
set grid y

# Produce smoother kdensity curves
set samples 1000

set linetype 1 linewidth 2 linecolor rgb '#20a010' pointtype 7
set linetype 2 linewidth 2 linecolor rgb '#f04040' pointtype 5

set style fill transparent solid 1
