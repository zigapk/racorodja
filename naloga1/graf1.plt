set title 'Prvih 200 točk zaporedja s_i'
set xlabel 'i'
set ylabel 's_i'

#set key above center horizontal enhanced autotitle
unset key

set terminal pdf enhanced
set output 'graf1.pdf'
plot 'zaporedje.dat' with points
