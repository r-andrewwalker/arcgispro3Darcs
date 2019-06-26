import math
import os
import arcpy

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

def arc_points(coords, d, bez_verts):

    gis_verts = []  # an empty list to store the final x,y,z vertices
    gis_verts.append([coords[0][0], coords[0][1], 0])  # first vertex, z value will be zero

    # Loop through the bezier vertices, and create a new x,y,z vertex. We can create a polyline out of these.
    for bez_xy in bez_verts:
        t = bez_xy[0] / d  # divide the x value by the total distance to get the position on the line (between 0 and 1)
        xt = (1 - t) * coords[0][0] + t * coords[1][0] # Find the x value for our GIS point
        yt = (1 - t) * coords[0][1] + t * coords[1][1] # Find the y value for our GIS point
        gis_verts.append([xt, yt, bez_xy[1]]) # Add the new x,y,z vertex to the list.

    gis_verts.append([coords[1][0], coords[1][1], 0])  # last vertex, z value will be zero

    return gis_verts

# Input data. We will create an arc between these locations
boulder = (476269, 4429846) # Coordinates in WGS84 UTM Zone 13N
denver = (500489, 4399441)

# Find the distance between the two locations
distance = distance( boulder[0], boulder[1], denver[0], denver[1] )

# Create points along a Bezier curve
bez_verts = bezier_vertices_quadratic( distance, 12 )

# Use the points from the Bezier curve to create vertices in geographic space
gis_verts = arc_points( [boulder, denver], distance, bez_verts)

# Set up the empty feature class that will store the arc
out_gdb = r'C:\GIS_DATA\example.gdb' # REPLACE WITH THE PATH TO YOUR GEODATABASE
sr = arcpy.SpatialReference(32613) # WGS84 UTM Zone 13N
arcpy.CreateFeatureclass_management(out_gdb, 'arc_boulder_denver', 'POLYLINE', '', 'DISABLED', 'ENABLED', sr)

# Create a Polyline arcpy object made up of Point arcpy objects
points_array = arcpy.Array()
for vertex in gis_verts:
    points_array.append(arcpy.Point(vertex[0], vertex[1], vertex[2]))
polyline = arcpy.Polyline( points_array, sr, True )

with arcpy.da.InsertCursor(os.path.join(out_gdb, 'arc_boulder_denver'), ['SHAPE@'] ) as cur:
    cur.insertRow( [polyline] )