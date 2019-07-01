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
        vertex = calc_point_on_bezier_2d([0, 0], [ d/2, 4000 ], [ d, 0 ], i / t_steps)
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

def ingest_od_data(table, start_x_field, start_y_field, end_x_field, end_y_field):
    od_data = []
    with arcpy.da.SearchCursor(table, [start_x_field, start_y_field, end_x_field, end_y_field]) as cur:
        for row in cur:
            od_data.append( [ [row[0], row[1]], [row[2], row[3]] ] )
    return od_data

sr = arcpy.SpatialReference(32613) # WGS84 UTM Zone 13N

# From an input table, create a list of origin-destination coordinate pairs. We can loop through these to create arcs.
source_data_table = r'C:\GIS_DATA\example.gdb\data' # REPLACE WITH THE PATH TO YOUR GEODATABASE TABLE

data = ingest_od_data(source_data_table, 'O_X', 'O_Y', 'D_X', 'D_Y')

# This list will store all of the Polyline objects
polylines = []

for start, end in data:
    # Find the distance between the two locations
    length = distance( start[0], start[1], end[0], end[1] )
    # Create points along a Bezier curve
    bez_verts = bezier_vertices_quadratic( length, 12 )
    # Use the points from the Bezier curve to create vertices in geographic space
    gis_verts = arc_points( [start, end], length, bez_verts )

    # Create a Polyline arcpy object made up of Point arcpy objects
    points_array = arcpy.Array()
    for vertex in gis_verts:
        points_array.append( arcpy.Point( vertex[0], vertex[1], vertex[2] ) )
    polyline = arcpy.Polyline( points_array, sr, True )
    polylines.append( polyline )

# Set up the empty feature class that will store the arcs
out_gdb = r'C:\GIS_DATA\example.gdb' # REPLACE WITH THE PATH TO YOUR GEODATABASE
arcpy.CreateFeatureclass_management(out_gdb, 'multiplearcs', 'POLYLINE', '', 'DISABLED', 'ENABLED', sr)

with arcpy.da.InsertCursor( os.path.join( out_gdb, 'multiplearcs' ), ['SHAPE@'] ) as cur:
    for polyline in polylines:
        cur.insertRow( [polyline] )
