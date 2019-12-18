"""
Example code:
Write legacy unstructured grid in 3D.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""


from writeParaview.legacy_unstructured import vtu
from MakeGrid import MakeGrid
import numpy as np
import os

# make output folder
if not os.path.isdir("output"): os.mkdir("output")

# 2D grid
x, y = MakeGrid()
SliceShape = x.shape
nx, ny = SliceShape

# 3rd dimension
nz =  20
dz = .25

# convert 2D to 3D: extrude a slice in 3rd direction
x = np.stack([x for _ in range(nz)], axis=-1)
y = np.stack([y for _ in range(nz)], axis=-1)
z = np.stack([np.zeros(SliceShape)+i*dz for i in range(nz)], axis=-1)

# make grid: convert structured grid to unstructured grid
xyz = np.zeros((x.size, 3))
xflat = x.flatten(order='F')
yflat = y.flatten(order='F')
zflat = z.flatten(order='F')
xyz[:,0] = xflat
xyz[:,1] = yflat
xyz[:,2] = zflat

# make cell connectivity array, 8-point cell
cells = np.zeros(((nx-1)*(ny-1)*(nz-1), 1+8), dtype=int)
cells[:,0] = 8
for k in range(nz-1):
    for j in range(ny-1):
        for i in range(nx-1):
            idx = i+j*(nx-1)+k*(nx-1)*(ny-1)
            cells[idx,1] = i+j*nx+k*nx*ny
            cells[idx,2] = i+j*nx+k*nx*ny + 1
            cells[idx,3] = i+j*nx+k*nx*ny + nx
            cells[idx,4] = i+j*nx+k*nx*ny + nx + 1
            cells[idx,5] = i+j*nx+k*nx*ny + nx*ny
            cells[idx,6] = i+j*nx+k*nx*ny + nx*ny + 1
            cells[idx,7] = i+j*nx+k*nx*ny + nx*ny + nx
            cells[idx,8] = i+j*nx+k*nx*ny + nx*ny + nx + 1
                  
cellTypes = np.zeros((nx-1)*(ny-1)*(nz-1), dtype=int)
cellTypes[:] = 11               # VTK_VOXEL (=11)

# make fields
p  = np.zeros((1,)+x.shape)
v2 = np.zeros((2,)+x.shape)
v3 = np.zeros((3,)+x.shape)

for j in range(p.shape[2]):
    p[:,:,j,:] = j
for i in range(v3.shape[1]):
    v3[0,i,:,:] = i
    v2[0,i,:,:] = i
for j in range(v3.shape[2]):
    v3[1,:,j,:] = j
    v2[1,:,j,:] = j
for k in range(v3.shape[3]):
    v3[2,:,:,k] = k 

p  = p.reshape((   p.size//p.shape[0],  p.shape[0]), order='F')
v2 = v2.reshape((v2.size//v2.shape[0], v2.shape[0]), order='F')
v3 = v3.reshape((v3.size//v3.shape[0], v3.shape[0]), order='F')

fields = {"Pressure":p, "V2":v2, "V3":v3}

vtu("output/Legacy_unstructured", xyz, cells, cellTypes, **fields)