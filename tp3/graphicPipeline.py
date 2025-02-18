import numpy as np

class Fragment:
  def __init__(self, x : int, y : int, depth : float):
    self.x = x
    self.y = y
    self.depth = depth

def edgeSide(p, v0, v1) : 
  return (p[0] - v0[0]) * (v1[1] - v0[1]) - (p[1] - v0[1]) * (v1[0] - v0[0])

class GraphicPipeline:
  def __init__ (self, width, height):
    self.width = width
    self.height = height
    self.depthBuffer = np.ones((height, width))

  def VertexShader(self, vertex, data) :
    outputVertex = np.zeros_like(vertex)
    x = vertex[0]
    y = vertex[1]
    z = vertex[2]
    w = 1.0


    vec = np.array([[x],[y],[z],[w]])
    vec = np.matmul(data['projMatrix'],np.matmul(data['viewMatrix'],vec))


    outputVertex[0] = vec[0]/vec[3]
    outputVertex[1] = vec[1]/vec[3]
    outputVertex[2] = vec[2]/vec[3]

    return outputVertex

  def computeAABox(self, v0, v1, v2) :
    minx = self.width/2 *(min(v0[0], v1[0], v2[0]) + 1) - 0.5
    miny = self.height/2 *(min(v0[1], v1[1], v2[1]) + 1) - 0.5
    maxx = self.width/2 *(max(v0[0], v1[0], v2[0]) + 1) - 0.5
    maxy = self.height/2 *(max(v0[1], v1[1], v2[1]) + 1) - 0.5

    return (minx, miny, maxx, maxy)


  def Rasterizer(self, v0, v1, v2, optimized=False) :
    fragments = []

    if optimized:
      minx, miny, maxx, maxy = self.computeAABox(v0, v1, v2)
      for j in range(int(miny), int(maxy)+1):
        for i in range(int(minx), int(maxx)+1):
          x = (i + 0.5)/self.width * 2 - 1
          y = (j + 0.5)/self.height * 2 - 1

          p = np.array([x,y,0])

          #check if the point is inside the triangle
          if (edgeSide(p, v0, v1) >= 0 and edgeSide(p, v1, v2) >= 0 and edgeSide(p, v2, v0) >= 0):
            # calculate the barycentric coordinates
            lamda0 = edgeSide(p, v1, v2) / edgeSide(v0, v1, v2)
            lamda1 = edgeSide(p, v2, v0) / edgeSide(v1, v2, v0)
            lamda2 = edgeSide(p, v0, v1) / edgeSide(v2, v0, v1)    

            # calculate the depth of the fragment
            depth = lamda0 * v0[2] + lamda1 * v1[2] + lamda2 * v2[2]

            # emit the fragment
            fragments.append(Fragment(i, j, depth))

    else:

      for j in range(0, self.height) : 
        for i in range(0, self.width) :
          x = (i + 0.5)/self.width * 2 - 1
          y = (j + 0.5)/self.height * 2 - 1

          p = np.array([x,y,0])

          #check if the point is inside the triangle
          if (edgeSide(p, v0, v1) >= 0 and edgeSide(p, v1, v2) >= 0 and edgeSide(p, v2, v0) >= 0):
            # calculate the barycentric coordinates
            lamda0 = edgeSide(p, v1, v2) / edgeSide(v0, v1, v2)
            lamda1 = edgeSide(p, v2, v0) / edgeSide(v1, v2, v0)
            lamda2 = edgeSide(p, v0, v1) / edgeSide(v2, v0, v1)    

            # calculate the depth of the fragment
            depth = lamda0 * v0[2] + lamda1 * v1[2] + lamda2 * v2[2]

            # emit the fragment
            fragments.append(Fragment(i, j, depth))
          
    
    
    return fragments



  def draw(self, vertices, triangles, data, optimized):
    self.newVertices = np.zeros_like(vertices)

    for i in range(vertices.shape[0]) :
       self.newVertices[i] = self.VertexShader(vertices[i],data)


    fragments = []
    for t in triangles :

      v0 = self.newVertices[t[0]]
      v1 = self.newVertices[t[1]]
      v2 = self.newVertices[t[2]]

      fragments += self.Rasterizer(v0, v1, v2, optimized)

    for f in fragments:
      x = f.x
      y = f.y
      if (self.depthBuffer[y,x] > f.depth):
        self.depthBuffer[y,x] = f.depth

      