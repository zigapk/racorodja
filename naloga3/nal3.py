import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# napisan s pomocjo primera iz https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html#scipy.integrate.odeint
def pend(y, t, b, c):
     theta, omega = y
     dydt = [omega, -b*omega - c*np.sin(theta)]
     return dydt

# koeficienti
betas = [0.02, 0.05, 0.1, 0.2]
colors = ['b', 'g', 'r', 'k']
y0 = [1.5, 0.0]
t = np.linspace(0, 200, num=400)

# odmik
for i, beta in enumerate(betas):
    sol = odeint(pend, y0, t, args=(beta, 1))
    plt.plot(t, sol[:, 0], colors[i], label=r'$\beta$ = ' + str(beta), linewidth=0.7)
    plt.legend(loc='best')

plt.xlabel(r'$ \tau $')
plt.ylabel(r'$ \phi $')
plt.grid()
plt.savefig('graf1.pdf')
plt.show()


# energija
for i, beta in enumerate(betas):
    sol = odeint(pend, y0, t, args=(beta, 1))
    e = 0.5*(sol[:, 1]**2) + (1-np.cos(sol[:, 0]))
    plt.semilogy(t, e, colors[i], label=r'$\beta$ = ' + str(beta), linewidth=0.7)
    plt.legend(loc='best')

plt.xlabel(r'$ \tau $')
plt.ylabel("W")
plt.savefig("graf2.pdf")
plt.show()
