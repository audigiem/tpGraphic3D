import numpy as np


class GraphicPipeline:

  def __init__ (self):
    self.newVertices = ()
    pass

  def VertexShader(self, vertex, data):
    viewMatrix = data['viewMatrix']
    projMatrix = data['projMatrix']

    vertex_h = np.append(vertex, 1)

    vertex_camera = viewMatrix @ vertex_h

    vertex_projected = projMatrix @ vertex_camera

    vertex_projected /= vertex_projected[3]

    return vertex_projected[:3]



  def draw(self, vertices, triangles, data):
    self.newVertices = np.zeros_like(vertices)

    for i in range(vertices.shape[0]) :
      self.newVertices[i] = self.VertexShader(vertices[i],data)
      pass
