import numpy as np
from exportToPly import write_ply_file
from math import cos, sin, pi

# vertices = np.array([
#     [0.0,0.0,0.0], #first vertex
#     [1.0,0.0,0.0], #second vertex
#     [0.0,1.0,0.0], #third vertex
#     [1.0,1.0,0.0]
#     ]
#                     )


vertices = np.array([
[0.0,0.0,0.0], #0
[1.0,0.0,0.0], #1
[0.0,1.0,0.0], #2
[1.0,1.0,0.0], #3
[0.0,0.0,1.0], #4
[1.0,0.0,1.0], #5
[0.0,1.0,1.0], #6
[1.0,1.0,1.0], #7
])


triangles = np.array([
    # Face inférieure (Z=0)
    [0, 2, 1], [1, 2, 3],  
    # Face supérieure (Z=1)
    [4, 5, 6], [5, 7, 6],  
    # Face avant (Y=0)
    [0, 1, 4], [1, 5, 4],  
    # Face arrière (Y=1)
    [2, 6, 3], [3, 6, 7],  
    # Face gauche (X=0)
    [0, 4, 2], [2, 4, 6],  
    # Face droite (X=1)
    [1, 3, 5], [3, 7, 5]   
], dtype=int)

# write_ply_file(vertices,triangles, 'triangle.ply' )


# generate a cylinder
pointPerRing = 10
nbRing = 4
height = 4
radius = 2

vertices = [[0.0, 0.0, 0.0]]

for i in range (nbRing) :
    z = i*(height / (nbRing -1))
    for j in range (pointPerRing) :
        theta = (j / pointPerRing) * 2 * pi 
        x = radius * cos(theta)
        y = radius * sin(theta)
        vertices.append([x,y,z])
        
vertices.append([0.0,0.0,nbRing])
vertices = np.array(vertices)


triangles = []


currentCenter = 0
for j in range(pointPerRing):
    current = j +1
    nextInRing = (j+1) % pointPerRing +1 
    triangles.append([currentCenter, nextInRing, current])

# outside surface
for i in range (nbRing):
        
    for j in range(pointPerRing):
        current = i * pointPerRing + j +1
        nextInRing = i * pointPerRing + (j+1) % pointPerRing +1
        above = (i+1) * pointPerRing + j +1
        aboveNext = (i+1) * pointPerRing + (j+1) % pointPerRing +1
        
        
        triangles.append([current, nextInRing, above])
        triangles.append([above, nextInRing, aboveNext])
        
currentCenter = len(vertices) - 1 
for j in range(pointPerRing):
    current = (nbRing-1) * pointPerRing + j +1
    nextInRing = (nbRing-1) * pointPerRing + (j+1) % pointPerRing +1
    triangles.append([current, nextInRing, currentCenter])           

        
triangles = np.array(triangles)

write_ply_file(vertices, triangles, 'cylinder.ply')