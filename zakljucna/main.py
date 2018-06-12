import sys
from sim import Sim
import numpy as np


def get_angle_range(sim, min_angle=0, max_angle=15, step=0.1, max_a=10 * 9.81, max_t=2500):
    valid_angles = []
    for angle in np.arange(min_angle, max_angle, step):
        sim.run(angle, angle)
        edge_values = sim.get_edge_values(angle)

        if edge_values['a'] < max_a and max_t > edge_values['t_contact'] > 0:
            valid_angles.append(angle)
    return valid_angles


# check for arguments
if len(sys.argv) < 3:
    print('Please provide planet and capsule name.')
    exit(1)
planet_name, capsule_name = sys.argv[1:3]

# init simulation environments
basic = Sim(planet_name, capsule_name, 80000, ignore_buoyancy=True)
realistic = Sim(planet_name, capsule_name, 80000)

# basic_range = get_angle_range(basic, step=0.01)
# realistic_range = get_angle_range(realistic, step=0.01)

# print(basic_range)
# print()
# print(realistic_range)

realistic.run(6.93, 6.93)
realistic.draw_scheme(6.93, 'all')
realistic.plot_height_over_time(6.93)
realistic.plot_height_over_x(6.93)
print('Max a:', '{:.2f}'.format(realistic.get_edge_values(6.93)['a']), '({:.2f} g)'.format(realistic.get_edge_values(6.93)['a'] / 9.81))

# run for dummy angle
# sim.run(4.7, uuid=0)
# realistic.run(6.9, uuid=0)
# sim.run(0, 1600000, uuid=0)

# 4.56 je kratek odboj

# 4.13 se odbije dvakrat
# 4.7 je skor optimaln entry kot

# print info about the flight:
# print('Parachute deployment height:', realistic.get_parachute_deployment_height(0))
# edge_values = realistic.get_edge_values(0)
# print('Max a:', '{:.2f}'.format(edge_values['a']), '({:.2f} g)'.format(edge_values['a'] / 9.81))
# print('Max P:', '{:.2f}'.format(edge_values['P']))

# draw scheme
# realistic.draw_scheme(0, 'landing')
# realistic.plot_height_over_time(0)
# realistic.plot_height_over_x(0)
# realistic.plot_velocity_over_time(0)

# soyuz podatki: http://wsn.spaceflight.esa.int/docs/Factsheets/35%20Soyuz%20LR.pdf
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.694.73&rep=rep1&type=pdf
# https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19690020179.pdf
# https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19670027745.pdf