import sys
from sim import Sim
import numpy as np
import matplotlib.pyplot as plt


def get_angle_range(sim, min_angle=0, max_angle=15, step=0.1, max_a=10 * 9.81, max_t=2500):
    valid_angles = []
    for angle in np.arange(min_angle, max_angle, step):
        sim.run(angle, angle)
        edge_values = sim.get_edge_values(angle)

        if edge_values['a'] < max_a and max_t > edge_values['t_contact'] > 0:
            valid_angles.append(angle)
    return valid_angles


def get_tex_table_line(sim, angle):
    edge_values = sim.get_edge_values(angle)
    result = "\t"
    result += "$ {0:.2f} $ & $ {1:.2f} $ & $ {2:.2f} $ \\\\".format(angle, edge_values['a'] / 9.81,
                                                                    edge_values['P'] / 1000)
    result += "\n"
    return result


def range_to_tex_table(angle_range, sim, step=0.3):
    result = "\t$ \phi_0\ [^\circ] $ & $a_{max}\ [g]$ & $ P_{max} \ [kW] $ \\\\\n\t\\hline\n"
    lasti = -1

    for i in range(0, len(angle_range), int(100 * step)):
        result += get_tex_table_line(sim, angle_range[i])
        lasti = i

    if lasti != len(angle_range) - 1:
        result += get_tex_table_line(sim, angle_range[-1])

    return result


def plot_range_for_velocity(v_min, v_max, step=500, save_to_file=None):
    vx, vy_min, vy_max = [], [], []
    for v in range(v_min, v_max, step):
        # print v to indicate progress
        print(v)
        # run sim for desired velocity
        sim = Sim(planet_name, capsule_name, 80000)
        sim.set_v0(v)
        rng = get_angle_range(sim, step=0.01)

        if len(rng) > 0:  # makes sure that even if it is impossible to land, the program won't crash after hours
            # store data
            vx.append(v)
            vy_min.append(rng[0])
            vy_max.append(rng[-1])

    # plot
    f, ax = plt.subplots(1)
    ax.plot(vx, vy_min, 'bo')
    ax.plot(vx, vy_max, 'ro')
    plt.xlabel('$ v_0 $ [m/s]')
    plt.ylabel('$ \phi_0 [°]$')
    plt.title(r'Min and max $ \phi_0(v_0) $')

    if save_to_file is not None:
        plt.savefig(save_to_file)

    plt.show()


# check for arguments
if len(sys.argv) < 3:
    print('Please provide planet and capsule name.')
    exit(1)
planet_name, capsule_name = sys.argv[1:3]

# init simulation environments
# basic = Sim(planet_name, capsule_name, 80000, ignore_buoyancy=True)
realistic = Sim(planet_name, capsule_name, 80000)

# basic_range = get_angle_range(basic, step=0.01)
realistic_range = get_angle_range(realistic, step=0.01)

# print(range_to_tex_table(basic_range, basic, step=0.2))
# print()
# print(range_to_tex_table(realistic_range, realistic, step=0.2))

# draw scheme
realistic.draw_scheme(4.15, 'planet', save_to_file='4_15_scheme.pdf')
# realistic.plot_height_over_time(5.8, save_to_file='5_8_height.pdf')
# realistic.plot_height_over_x(5.8, save_to_file='5_8_height_over_x.pdf')
# realistic.plot_velocity_over_time(5.8, save_to_file='5_8_velocity.pdf')

# plot range for initial velocities
# plot_range_for_velocity(8000, 12001, step=200, save_to_file='range_of_velocity.pdf')

# 4.56 je kratek odboj
# 4.13 se odbije dvakrat
# 4.7 je skor optimaln entry kot
