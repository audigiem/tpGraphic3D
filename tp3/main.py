#! /usr/bin/env python3

import numpy as np
import time

from graphicPipeline import GraphicPipeline
width = 1280  
height = 720
pipeline = GraphicPipeline(width,height)

from camera import Camera
position = np.array([1.1,1.1,1.1])
lookAt = np.array([-0.577,-0.577,-0.577])
up = np.array([0.33333333,  0.33333333, -0.66666667])
right = np.array([-0.57735027,  0.57735027,  0.])
cam = Camera(position, lookAt, up, right)

from projection import Projection
nearPlane = 0.1
farPlane = 10.0
fov = 1.91986
aspectRatio = width/height
proj = Projection(nearPlane ,farPlane,fov, aspectRatio) 

vertices = np.array([
  [0.0,0.0,0.0], #0max(v0[1], v1[1], v2[1])
  [1.0,0.0,0.0], #1
  [0.0,1.0,0.0], #2 
  [1.0,1.0,0.0], #3 
  [0.0,0.0,1.0], #4 
  [1.0,0.0,1.0], #5 
  [0.0,1.0,1.0], #6
  [1.0,1.0,1.0], #7
])

triangles = np.array([
  [1,0,2],
  [3,1,2],
  [4,5,6],
  [5,7,6],
  [0,1,4],
  [4,1,5],
  [2,6,3],
  [3,6,7],
  [0,6,2],
  [4,6,0],
  [1,3,7],
  [5,1,7]
], dtype=int)

data = dict([
  ('viewMatrix',cam.getMatrix()),
  ('projMatrix',proj.getMatrix())
])

time1 = time.time()

pipeline.draw(vertices, triangles, data, False)

time2 = time.time()
print("Rasterizer and depth buffer in : ", time2-time1)

import matplotlib.pyplot as plt
imgplot = plt.imshow(1/pipeline.depthBuffer, cmap='gray')
plt.show()


pipeline.draw(vertices, triangles, data, True)
time3 = time.time()
print("Rasterizer and depth buffer optimized in : ", time3-time2)

imgplot = plt.imshow(1/pipeline.depthBuffer, cmap='gray')
plt.show()