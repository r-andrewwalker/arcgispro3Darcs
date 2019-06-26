import math
import matplotlib.pyplot as plt


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calc_point_on_bezier_2d(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return [x, y]


def bezier_vertices_quadratic(d, t_steps):
    bezier_vertices = []
    for i in range(1, t_steps):
        vertex = calc_point_on_bezier_2d([0, 0], [ d/2, d/2 ], [ d, 0 ], i / t_steps)
        bezier_vertices.append(vertex)
    return bezier_vertices


# Modify the second parameter to change the number of vertices
verts = bezier_vertices_quadratic(1000, 12)


plt.plot([x[0] for x in verts], [y[1] for y in verts] )
for i in verts:
    plt.plot(i[0], i[1], 'ro')
plt.ylabel('Height')
plt.xlabel('Distance along curve')
#plt.xticks([0, 20, 40, 60, 80, 100])
plt.show()