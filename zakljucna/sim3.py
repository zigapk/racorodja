import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from matplotlib.patches import Ellipse

# check for arguments
if len(sys.argv) < 3:
    print('Please provide planet and capsule name.')
    exit(1)

planet_name, capsule_name = sys.argv[1:3]

# read the config
with open('params.json', 'r') as f:
    params = json.loads(f.read())
    global_params = params['global']
    planet = params['planets'][planet_name]
    capsule = params['capsules'][capsule_name]

# calculate H
global_params['H'] = global_params['R'] * planet['T'] / (planet['M'] * planet['g0'])

# prepare dict to store edge values
edge_values = {}


# helpers
def deg2rad(phi): return phi * np.pi / 180


def rad2deg(r): return r / np.pi * 180


def g(h):
    return planet['g0'] * (planet['r'] / (planet['r'] + h)) ** 2


def rho(h):
    return planet['rho0'] * np.e ** (-h / global_params['H'])


def split_parts(a):
    # return a, []
    # strip the underground part
    i = len(a) - 1
    for j in range(len(a)):
        if a[j][1] <= 0:
            i = j
            break
    a = a[:i]

    # split at the speed of parachute deployment
    for j in range(len(a)):
        if a[j][2] < capsule['max_parachute_v'] and a[j][1] < capsule['h0']:
            return a[:j], a[j:]


def ratio(new_r, x):
    return (x * new_r) / planet['r']


def movement(parametres, t, uuid):
    global edge_values
    x, h, v, b, phi = parametres

    dxdt = v * np.cos(b)
    dhdt = -v * np.sin(b)
    dvdt = g(h) * np.sin(b) - rho(h) * capsule['k'] * v ** 2
    dbdt = g(h) * np.cos(b) / v - v * np.cos(b) / planet['r']
    dphidt = v * np.cos(b) / (planet['r'] + h)

    p = v * rho(h) * capsule['k'] * v ** 2

    # store edge values
    if uuid not in edge_values.keys():
        edge_values[uuid] = {'a': 0, 'P': 0}

    # check for a
    if abs(dvdt) > edge_values[uuid]['a']:
        edge_values[uuid]['a'] = abs(dvdt)

    # check P
    if p > edge_values[uuid]['P']:
        edge_values[uuid]['P'] = p

    return [dxdt, dhdt, dvdt, dbdt, dphidt]


t = np.linspace(0, 1600000, 1600000)
# t = np.linspace(0, 800000, 800000)

# 4.13 se odbije dvakrat
# 4.7 je skor optimaln entry kot
sol = odeint(movement, [0, capsule['h0'], capsule['v0'], deg2rad(5), 0], t, args=(0,))
normal, schute = split_parts(sol)

# draw
new_R = 9
circles = [
    ('b', 0.3,
     Ellipse(xy=(0, 0), width=2 * (new_R + ratio(new_R, capsule['h0'])),
             height=2 * (new_R + ratio(new_R, capsule['h0'])),
             angle=360)),
    ('#9E9E9E', 1, Ellipse(xy=(0, 0), width=2 * new_R, height=2 * new_R, angle=360)),
]
fig = plt.figure(0, figsize=(15, 15))
ax = fig.add_subplot(111, aspect='equal')

for c in circles:
    ax.add_artist(c[2])
    c[2].set_clip_box(ax.bbox)
    c[2].set_alpha(c[1])
    c[2].set_facecolor(c[0])

plt.axis('off')

# CLOSEUPS
# normal
ax.set_xlim(-0.2, 3.5)
ax.set_ylim(8, 9.5)

# landing
# ax.set_xlim(2.7, 3)
# ax.set_ylim(8.4, 8.8)

# whole earth
# ax.set_xlim(-20, 20)
# ax.set_ylim(-20, 20)


# print info about the flight:
print('Parachute deployment height:', int(round(schute[0][1])) if len(schute) else '/')
print('Max a:', '{:.2f}'.format(edge_values[0]['a']), '({:.2f} g)'.format(edge_values[0]['a'] / 9.81))
print('Max P:', '{:.2f}'.format(edge_values[0]['P']))

ax.plot([ratio(new_R, np.sin(i[4]) * (planet['r'] + i[1])) for i in normal],
        [ratio(new_R, np.cos(i[4]) * (planet['r'] + i[1])) for i in normal],
        'ko-', markersize=0.4)

ax.plot([ratio(new_R, np.sin(i[4]) * (planet['r'] + i[1])) for i in schute],
        [ratio(new_R, np.cos(i[4]) * (planet['r'] + i[1])) for i in schute],
        'go-', markersize=0.4)

plt.show()
