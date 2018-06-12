import json
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


# helpers
def deg2rad(phi): return phi * np.pi / 180


def rad2deg(r): return r / np.pi * 180


# movement function for physics simulation (must be outside the class to not automatically be passed self as first arg)
def movement(parametres, t, sim, uuid):
    x, h, v, b, phi = parametres

    dxdt = v * np.cos(b)
    dhdt = -v * np.sin(b)
    dvdt = sim.g(h) * np.sin(b) - sim.rho(h) * sim.capsule['k'] * v ** 2
    dbdt = sim.g(h) * np.cos(b) / v - v * np.cos(b) / sim.planet['r']
    if not sim.ignore_buoyancy:
        dbdt -= sim.rho(h) * v * sim.capsule['k'] * sim.capsule['l2d']

    dphidt = v * np.cos(b) / (sim.planet['r'] + h)

    p = v * sim.rho(h) * sim.capsule['k'] * v ** 2

    # store edge values
    if uuid not in sim.edge_values.keys():
        sim.edge_values[uuid] = {'a': 0, 'P': 0, 't_contact': -1}

    # check for a
    if abs(dvdt) > sim.edge_values[uuid]['a']:
        sim.edge_values[uuid]['a'] = abs(dvdt)

    # check P
    if p > sim.edge_values[uuid]['P']:
        sim.edge_values[uuid]['P'] = p

    # check h
    if h <= 0 and sim.edge_values[uuid]['t_contact'] < 0:
        sim.edge_values[uuid]['t_contact'] = t

    return [dxdt, dhdt, dvdt, dbdt, dphidt]


class Sim:
    def __init__(self, planet_name, capsule_name, t, ignore_buoyancy=False, config_file='params.json'):
        # read the config
        with open(config_file, 'r') as f:
            self.params = json.loads(f.read())
            self.global_params = self.params['global']
            self.planet = self.params['planets'][planet_name]
            self.capsule = self.params['capsules'][capsule_name]

        # save some config
        self.ignore_buoyancy = ignore_buoyancy

        # calculate H
        self.global_params['H'] = self.global_params['R'] * self.planet['T'] / (self.planet['M'] * self.planet['g0'])

        # drag k
        self.capsule['k'] = self.capsule['S'] * self.capsule['k_drag'] / (2 * self.capsule['m'])

        # prepare dict to store simulation results
        self.simulations = {}

        # prepare dict to store edge values
        self.edge_values = {}

        # prepare t linear space
        self.t = np.linspace(0, t, t)

    def g(self, h):
        return self.planet['g0'] * (self.planet['r'] / (self.planet['r'] + h)) ** 2

    def rho(self, h):
        return self.planet['rho0'] * np.e ** (-h / self.global_params['H'])

    def get_coordinates(self, point, new_r):
        x = self.ratio(new_r, np.sin(point[4]) * (self.planet['r'] + point[1]))
        y = self.ratio(new_r, np.cos(point[4]) * (self.planet['r'] + point[1]))
        return x, y

    def split_parts(self, a):
        # strip the underground part
        i = len(a) - 1
        for j in range(len(a)):
            if a[j][1] <= 0:
                i = j
                break
        a = a[:i]

        # split at the speed of parachute deployment
        for j in range(len(a)):
            if a[j][2] < self.capsule['max_parachute_v'] and a[j][1] < self.capsule['h0']:
                return a[:j], a[j:]

        return a, []

    def run(self, angle, uuid):
        solution = odeint(movement, [0, self.capsule['h0'], self.capsule['v0'], deg2rad(angle), 0], self.t,
                          args=(self, uuid))
        fast, parachute = self.split_parts(solution)
        self.simulations[uuid] = (fast, parachute, solution, angle)

        return fast, parachute

    def ratio(self, new_r, x):
        return (x * new_r) / self.planet['r']

    def get_sim(self, uuid):
        return self.simulations[uuid]

    def get_edge_values(self, uuid):
        return self.edge_values[uuid]

    def get_parachute_deployment_height(self, uuid):
        return int(round(self.get_sim(uuid)[1][0][1])) if len(self.get_sim(uuid)[1]) else '/'

    def draw_scheme(self, uuid, view, new_r=9, size=(15, 15), save_to_file=None):
        # draw planet and atmosphere
        circles = [
            ('b', 0.3,
             Ellipse(xy=(0, 0), width=2 * (new_r + self.ratio(new_r, self.planet['h0'])),
                     height=2 * (new_r + self.ratio(new_r, self.planet['h0'])),
                     angle=360)),
            (self.planet['color'], 1, Ellipse(xy=(0, 0), width=2 * new_r, height=2 * new_r, angle=360)),
        ]

        # we are drawing earth, let's draw some continents
        if self.planet['g0'] == 9.81:
            circles.append(('#2E7D32', 1, Ellipse(xy=(3, -2), width=5, height=7, angle=50)))
            circles.append(('#2E7D32', 1, Ellipse(xy=(3, -5), width=3, height=4, angle=-33)))
            circles.append(('#2E7D32', 1, Ellipse(xy=(-2, 5), width=6, height=7, angle=-33)))
            circles.append(('#2E7D32', 1, Ellipse(xy=(-1.1, 1.3), width=1.7, height=3, angle=45)))
            circles.append(('#2E7D32', 1, Ellipse(xy=(8.3, 1), width=1, height=5, angle=8)))

        fig = plt.figure(0, figsize=size)
        ax = fig.add_subplot(111, aspect='equal')

        for c in circles:
            ax.add_artist(c[2])
            c[2].set_clip_box(ax.bbox)
            c[2].set_alpha(c[1])
            c[2].set_facecolor(c[0])

        plt.axis('off')

        sim = self.get_sim(uuid)

        if view == 'landing':
            y_margin = 0.15
            x_margin = 0.15
            center = self.get_coordinates(sim[1][-1], new_r)
            ax.set_xlim(center[0] - x_margin, center[0] + x_margin)
            ax.set_ylim(center[1] - y_margin, center[1] + y_margin)
        elif view == 'all':
            coordinates = [self.get_coordinates(i, new_r) for i in sim[0]]
            x_margin = 0.3
            y_margin = 0.3
            ax.set_xlim(min(coordinates, key=lambda x: x[0])[0] - x_margin,
                        max(coordinates, key=lambda x: x[0])[0] + x_margin)
            ax.set_ylim(min(coordinates, key=lambda x: x[1])[1] - y_margin,
                        max(coordinates, key=lambda x: x[1])[1] + y_margin)
        elif view == 'planet':
            margin = 5
            ax.set_xlim(-new_r - margin, new_r + margin)
            ax.set_ylim(-new_r - margin, new_r + margin)

        ax.plot([self.get_coordinates(i, new_r)[0] for i in sim[0]],
                [self.get_coordinates(i, new_r)[1] for i in sim[0]],
                'ko-', markersize=0.4)

        ax.plot([self.get_coordinates(i, new_r)[0] for i in sim[1]],
                [self.get_coordinates(i, new_r)[1] for i in sim[1]],
                'go-', markersize=0.4)

        plt.title(r'$ \phi_0 $ = ' + '{:.2f}°'.format(sim[3]), fontsize=40)

        if save_to_file is not None:
            plt.savefig(save_to_file)

        plt.show()

    def plot_height_over_time(self, uuid, save_to_file=None):
        # gather data
        _, _, data, angle = self.get_sim(uuid)

        # plot
        f, ax = plt.subplots(1)
        ax.plot(self.t, data[:, 1], 'k')
        plt.xlabel('t [s]')
        plt.ylabel('h [m]')
        plt.title(r'h(t) for $ \phi_0 $ = ' + '{:.2f}°'.format(angle))

        ax.set_xlim(xmin=0, xmax=self.get_edge_values(uuid)['t_contact'] + 10)
        ax.set_ylim(ymin=0)

        if save_to_file is not None:
            plt.savefig(save_to_file)

        plt.show()

    def plot_height_over_x(self, uuid, save_to_file=None):
        # gather data
        _, _, data, angle = self.get_sim(uuid)

        # plot
        f, ax = plt.subplots(1)
        ax.plot(data[:, 0], data[:, 1], 'k')
        plt.xlabel('x [m]')
        plt.ylabel('h [m]')
        plt.title(r'h(x) for $ \phi_0 $ = ' + '{:.2f}°'.format(angle))

        ax.set_xlim(xmin=0, xmax=data[-1][0] + 100000)
        ax.set_ylim(ymin=0)

        if save_to_file is not None:
            plt.savefig(save_to_file)

        plt.show()

    def plot_velocity_over_time(self, uuid, save_to_file=None):
        # gather data
        _, _, data, angle = self.get_sim(uuid)

        # plot
        f, ax = plt.subplots(1)
        ax.plot(self.t, data[:, 2], 'k')
        plt.xlabel('t [s]')
        plt.ylabel('v [m/s]')
        plt.title(r'v(t) for $ \phi_0 $ = ' + '{:.2f}°'.format(angle))

        ax.set_xlim(xmin=0, xmax=self.get_edge_values(uuid)['t_contact'] + 10)
        ax.set_ylim(ymin=0)

        if save_to_file is not None:
            plt.savefig(save_to_file)

        plt.show()
