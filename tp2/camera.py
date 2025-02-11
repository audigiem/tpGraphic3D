import numpy as np

class Camera:
  def __init__(self, position, lookAt, up, right) :
    self.position = position
    self.lookAt = lookAt
    self.up = up
    self.right = right

  def getMatrix(self):
    forward = self.lookAt / np.linalg.norm(self.lookAt)
    right = self.right / np.linalg.norm(self.right)
    up = self.up / np.linalg.norm(self.up)

    R = np.array([
      [right[0], up[0], -forward[0], 0],
      [right[1], up[1], -forward[1], 0],
      [right[2], up[2], -forward[2], 0],
      [0, 0, 0, 1]
    ])

    T = np.array([
      [1, 0, 0, -self.position[0]],
      [0, 1, 0, -self.position[1]],
      [0, 0, 1, -self.position[2]],
      [0, 0, 0, 1]
    ])

    return R @ T
