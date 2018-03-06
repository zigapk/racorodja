set title 'Prvih 200 točk zaporedja s_i'
set xlabel 'i'
set ylabel 's_i'

unset key

set terminal pdf enhanced
set output 'graf1.pdf'
plot 'zaporedje.dat' with points
