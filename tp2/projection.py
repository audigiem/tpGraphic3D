import numpy as np

class Projection:
  def __init__(self, near,far,fov,aspectRatio) :
    self.nearPlane = near
    self.farPlane = far
    self.fov = fov
    self.aspectRatio = aspectRatio

  def getMatrix(self):
    f = 1.0 / np.tan(self.fov / 2)
    near, far = self.nearPlane, self.farPlane

    return np.array([
      [f / self.aspectRatio, 0, 0, 0],
      [0, f, 0, 0],
      [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
      [0, 0, -1, 0]
    ])