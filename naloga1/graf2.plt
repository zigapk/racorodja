set encoding utf8
set title 'Amplituda v odvisnosti od vsiljene frekvence'
set xlabel 'frekvenca [Hz]'
set ylabel 'amplituda'
unset key

# A
# w ... omega
# b ... beta
# r ... omega0
f(x) = A / abs(-x**2 - 2*beta*x*{0, 1} + omega0**2)

fit f(x) 'resonanca.dat' via A, beta, omega0

set terminal png enhanced
set output 'graf2.png'
plot 'resonanca.dat' with points, f(x)
