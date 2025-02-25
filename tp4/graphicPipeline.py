import numpy as np


class Fragment:
    def __init__(self, x : int, y : int, depth : float, interpolated_data ):
        self.x = x
        self.y = y
        self.depth = depth
        self.interpolated_data = interpolated_data
        self.output = []

def edgeSide(p, v0, v1) : 
    return (p[0]-v0[0])*(v1[1]-v0[1]) - (p[1]-v0[1])*(v1[0]-v0[0])

def edgeSide3D(p,v0,v1) :
    return np.linalg.norm(np.cross(p[0:3]-v0[0:3],v1[0:3]-v0[0:3]))

def sample(texture, u, v) :
    u = int(u*texture.shape[0])
    v = int((1-v)*texture.shape[1])
    return texture[v,u] / 255.0

class GraphicPipeline:
    def __init__ (self, width, height):
        self.width = width
        self.height = height
        self.image = np.zeros((height, width, 3))
        self.depthBuffer = np.ones((height, width))


    def VertexShader(self, vertex, data) :
        outputVertex = np.zeros(14)

        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        w = 1.0

        vec = np.array([[x],[y],[z],[w]])

        vec = np.matmul(data['projMatrix'],np.matmul(data['viewMatrix'],vec))

        outputVertex[0] = vec[0]/vec[3]
        outputVertex[1] = vec[1]/vec[3]
        outputVertex[2] = vec[2]/vec[3]
        
        L = data['lightPosition'] - vertex[0:3]
        V = data['cameraPosition'] - vertex[0:3]
        N = vertex[3:6]
        outputVertex[3:6] = L
        outputVertex[6:9] = V
        outputVertex[9:12] = N
        outputVertex[12:14] = vertex[6:8]
    
        return outputVertex


    def Rasterizer(self, v0, v1, v2) :
        fragments = []

        #culling back face
        area = edgeSide(v0,v1,v2)
        area3D = edgeSide3D(v0,v1,v2)
        if area < 0 :
            return fragments
        
        
        #AABBox computation
        #compute vertex coordinates in screen space
        v0_image = np.array([0,0])
        v0_image[0] = (v0[0]+1.0)/2.0 * self.width 
        v0_image[1] = ((v0[1]+1.0)/2.0) * self.height 

        v1_image = np.array([0,0])
        v1_image[0] = (v1[0]+1.0)/2.0 * self.width 
        v1_image[1] = ((v1[1]+1.0)/2.0) * self.height 

        v2_image = np.array([0,0])
        v2_image[0] = (v2[0]+1.0)/2.0 * self.width 
        v2_image[1] = (v2[1]+1.0)/2.0 * self.height 

        #compute the two point forming the AABBox
        A = np.min(np.array([v0_image,v1_image,v2_image]), axis = 0)
        B = np.max(np.array([v0_image,v1_image,v2_image]), axis = 0)

        #cliping the bounding box with the borders of the image
        max_image = np.array([self.width-1,self.height-1])
        min_image = np.array([0.0,0.0])

        A  = np.max(np.array([A,min_image]),axis = 0)
        B  = np.min(np.array([B,max_image]),axis = 0)
        
        #cast bounding box to int
        A = A.astype(int)
        B = B.astype(int)
        #Compensate rounding of int cast
        B = B + 1

        #for each pixel in the bounding box
        for j in range(A[1], B[1]) : 
           for i in range(A[0], B[0]) :
                x = (i+0.5)/self.width * 2.0 - 1 
                y = (j+0.5)/self.height * 2.0 - 1

                p = np.array([x,y])
                
                area0 = edgeSide(p,v0,v1)
                area1 = edgeSide(p,v1,v2)
                area2 = edgeSide(p,v2,v0)

                #test if p is inside the triangle
                if (area0 >= 0 and area1 >= 0 and area2 >= 0) : 
                    
                    #Computing 2d barricentric coordinates
                    lambda0 = area1/area
                    lambda1 = area2/area
                    lambda2 = area0/area
                    
                    #one_over_z = lambda0 * 1/v0[2] + lambda1 * 1/v1[2] + lambda2 * 1/v2[2]
                    #z = 1/one_over_z
                    
                    z = lambda0 * v0[2] + lambda1 * v1[2] + lambda2 * v2[2]

                    p = np.array([x,y,z])
                    
                    #Recomputing the barricentric coordinaties for vertex interpolation
                    area0 = edgeSide3D(p,v0,v1)
                    area1 = edgeSide3D(p,v1,v2)
                    area2 = edgeSide3D(p,v2,v0)

                    lambda0 = area1/area3D
                    lambda1 = area2/area3D
                    lambda2 = area0/area3D
                    
                    l = v0.shape[0]
                    #interpolating
                    interpolated_data = v0[3:l] * lambda0 + v1[3:l] * lambda1 + v2[3:l] * lambda2
                    
                    #Emiting Fragment
                    fragments.append(Fragment(i,j,z,interpolated_data))
                    

        return fragments
    
    def fragmentShader(self,fragment,data):
        color = np.array([1,1,1]) 
        L,V,N = fragment.interpolated_data[0:3],fragment.interpolated_data[3:6],fragment.interpolated_data[6:9]
        L,V,N = L/np.linalg.norm(L),V/np.linalg.norm(V),N/np.linalg.norm(N)
        
        # phong shading
        ambient = 0.1
        alpha = 32
        ki = 0.1
        kd = 0.9
        ks = 0.3
        modelColor = np.array([1,1,1])
        
        diffuse = np.max([0,np.dot(L,N)])
        specular = np.max([0,np.dot(N,(L+V)/np.linalg.norm(L+V))])**alpha
        
        phong = ambient * ki + kd * diffuse + ks * specular
        objectColor = sample(data['texture'],fragment.interpolated_data[9],fragment.interpolated_data[10])
        # color = np.ceil(color * phong * 4)/4
        fragment.output = color * phong * objectColor

        pass

    def draw(self, vertices, triangles, data):
        #Calling vertex shader
        self.newVertices = np.zeros((vertices.shape[0], 14))

        for i in range(vertices.shape[0]) :
            self.newVertices[i] = self.VertexShader(vertices[i],data)
        
        fragments = []
        #Calling Rasterizer
        for i in triangles :
            fragments.extend(self.Rasterizer(self.newVertices[i[0]], self.newVertices[i[1]], self.newVertices[i[2]]))
        
        for f in fragments:

            #Calling fragment shader
            self.fragmentShader(f,data)
            
            #depth test
            if self.depthBuffer[f.y][f.x] > f.depth : 
                self.depthBuffer[f.y][f.x] = f.depth
                
                self.image[f.y][f.x] = f.output
                
            

