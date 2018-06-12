import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

degtorad = lambda phi: phi * np.pi / 180
radtodeg = lambda r: r / np.pi * 180

g0 = 9.81
R = 6378000
R_gas = 8314
T = 236.7
mi = 28.95
H = R_gas * T / (mi * g0)
rho0 = 1.225
k = 1.344e-3


# zacetni parametri
h0 = 100000
v0 = 11000


def g(h):
    return g0 * (R / (R + h)) ** 2


def rho(h):
    return rho0 * np.e ** (-h / H)


def movement(parametres, t):
    x, h, v, b, phi = parametres

    dxdt = v * np.cos(b)
    dhdt = -v * np.sin(b)
    dvdt = g(h) * np.sin(b) - rho(h) * k * v ** 2
    dbdt = g(h) * np.cos(b) / v - v * np.cos(b) / R
    dphidt = v * np.cos(phi) / (R + h)

    print(t, '\t\t', dbdt, '\t', b)
    # if rho(h) < 0: print('panika')
    return [dxdt, dhdt, dvdt, dbdt, dphidt]


t = np.linspace(0, 800, 800)
sol = odeint(movement, [0, h0, v0, degtorad(4.7), 0], t)

f, ax = plt.subplots(1)
ax.plot(sol[:, 0], sol[:, 1], 'b', linewidth=0.9)

ax.set_ylim(ymin=0)
plt.show()
