import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def draw(points, save_file_name=None):
    # separate inner and outer points
    inner = np.array([i for i in points if (i[0]**2 + i[1]**2)**0.5 < 1])
    outer = np.array([i for i in points if (i[0]**2 + i[1]**2)**0.5 >= 1])

    # circle
    circle = lambda t: [np.cos(t), np.sin(t)]
    x, y = circle(np.linspace(0, 2*np.pi, 1000))

    # graph configuration
    fig = plt.figure(figsize=(6,6))
    fig.suptitle('Naključne točke iz enotkskega kvadrata znotraj enotskega kroga')
    left, bottom, width, height = [0.15, 0.15, 0.7, 0.7]
    ax = fig.add_axes([left, bottom, width, height])
    ax.set_xlabel('$x_i$')
    ax.set_ylabel('$y_i$')

    # plot series
    ax.plot(x, y, 'k', linewidth=1.0)
    ax.scatter(inner[:,0], inner[:,1], s=1, color='r')
    ax.scatter(outer[:,0], outer[:,1], s=1)

    # legend
    plt.legend(handles=[
        mpatches.Patch(color='red', label='Točke znotraj enotskega kroga'),
        mpatches.Patch(color='blue', label='Točke zunaj enotskega kroga')
    ],bbox_to_anchor=(0., 1.02, 1., .102), loc=3, mode="expand", borderaxespad=0.)

    if save_file_name:
        fig.savefig(save_file_name)

    plt.show()

def generate(seed, n=10000):
    points, m = [], 0

    random.seed(seed)

    for _ in range(n):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        points.append((x, y))
        if (x**2 + y**2)**0.5 < 1:
            m += 1

    return 4*m/n, points

# pick the first random seed to later generate graph with
graph_seed = random.random()

with open('rezultati.dat', 'w') as f:
    f.write('ZRNO,R\n')
    for i in range(10):
        r, _ = generate(i+1)
        f.write('{},{}\n'.format(i+1, r))

_, points = generate(graph_seed)
draw(points, save_file_name='scatter.pdf')
