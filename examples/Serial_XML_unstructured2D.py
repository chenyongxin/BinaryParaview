"""
Example code:
Write serial XML unstructured grid in 2D.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.xml_unstructured import vtu
from grid.MakeGrid import MakeGrid
import numpy as np
import os

# make output folder
if not os.path.isdir("output"): os.mkdir("output")

# get 2D grid
x, y = MakeGrid()
# get dimension info
nx, ny = x.shape

# make grid: convert structured grid to unstructured grid
xyz = np.zeros((x.size, 3))
xflat = x.flatten(order='F')
yflat = y.flatten(order='F')
xyz[:,0] = xflat
xyz[:,1] = yflat

# make cell connectivity array, 4-point cell
cells = np.zeros(((nx-1)*(ny-1), 1+4), dtype=int)
cells[:,0] = 4
for j in range(ny-1):
    for i in range(nx-1):
        idx = i+j*(nx-1)
        cells[idx,1] = i+j*nx
        cells[idx,2] = i+j*nx + 1
        cells[idx,3] = i+j*nx + nx
        cells[idx,4] = i+j*nx + nx + 1

cellTypes = np.zeros((nx-1)*(ny-1), dtype=int)
cellTypes[:] = 8               # VTK_PIXEL (=8)

# make fields
p  = np.zeros((1,)+x.shape)
v2 = np.zeros((2,)+x.shape)

for j in range(p.shape[2]):
    p[:,:,j] = j
for i in range(p.shape[1]):
    v2[0,i,:] = i
for j in range(p.shape[2]):
    v2[1,:,j] = j

p  = p.reshape((p.size, 1), order='F')
v2 = v2.reshape((v2.size//2, 2), order='F')

fields = {"Pressure":p, "V2":v2}

vtu("output/Serial_XML_unstructured2D", xyz, cells, cellTypes, **fields)
