"""
Example code:
Write parallel XML unstructured grid in 3D.

Only 1D decomposision is used. 

To execuate this code, run command in terminal (Linux/Mac) or cmd (Windows):
mpiexec -n 3 python Parallel_XML_unstructured.py

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.xml_unstructured import pvtu
from MakeGrid import MakeGrid
from mpi4py import MPI
import numpy as np
import os, sys

# init MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
master = rank == 0
# check the odd number
if size != 3: sys.exit("Abort: use 3 processors to run this example code.")

# define pathes
pvtuDir = "output/"         # path to save .pvts file
vtuDir  = "output/data/"    # path to save .vts files
relativeDir =    "data/"    # relative path from .pvts to .vts
pvtuName = pvtuDir + "Parallel_XML_unstructured" 
pieceName = "Seial_XML_unstructured_Piece"
vtuName = vtuDir + pieceName                    
relativePath = relativeDir + pieceName

# make output folder
if master:
    if not os.path.isdir(pvtuDir): os.mkdir(pvtuDir)
    if not os.path.isdir(vtuDir): os.mkdir(vtuDir)
    
# Make global grid
# 2D grid
nx = 120+1
ny = 60+1
x, y = MakeGrid(nx, ny)

# 3rd dimension
nz =  20+1
dz = .25

# extrude
x = np.stack([x for _ in range(nz)], axis=-1)
y = np.stack([y for _ in range(nz)], axis=-1)
z = np.stack([np.zeros((nx, ny))+i*dz for i in range(nz)], axis=-1)

# number of cells in partition
pcx = (nx-1)//size    
pcy =  ny-1
pcz =  nz-1

# make grid: convert structured grid to unstructured grid
xyz = np.zeros( (((nx-1)//size+1)*ny*nz, 3) )
xflat = x.copy()[ (nx-1)//size*rank : (nx-1)//size*(rank+1)+1, :, : ].flatten(order='F')
yflat = y.copy()[ (nx-1)//size*rank : (nx-1)//size*(rank+1)+1, :, : ].flatten(order='F')
zflat = z.copy()[ (nx-1)//size*rank : (nx-1)//size*(rank+1)+1, :, : ].flatten(order='F')
xyz[:,0] = xflat
xyz[:,1] = yflat
xyz[:,2] = zflat

# make local cell connectivity array, 8-point cell
cells = np.zeros(((nx-1)//size*(ny-1)*(nz-1), 1+8), dtype=int)
cells[:,0] = 8

for k in range(pcz):
    for j in range(pcy):
        for i in range(pcx):
            idx = i+j*pcx+k*pcx*pcy
            cells[idx,1] = i+j*(pcx+1)+k*(pcx+1)*ny
            cells[idx,2] = i+j*(pcx+1)+k*(pcx+1)*ny + 1
            cells[idx,3] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1)
            cells[idx,4] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1) + 1
            cells[idx,5] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1)*ny
            cells[idx,6] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1)*ny + 1
            cells[idx,7] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1)*ny + (pcx+1)
            cells[idx,8] = i+j*(pcx+1)+k*(pcx+1)*ny + (pcx+1)*ny + (pcx+1) + 1
            
cellTypes = np.zeros((nx-1)//size*(ny-1)*(nz-1), dtype=int)
cellTypes[:] = 11               # VTK_VOXEL (=11)

# make a local scalar field
p = np.zeros((1, (nx-1)//size+1, ny, nz))
for k in range(nz):
    for j in range(ny):
        for i in range((nx-1)//size+1):
            p[:, i, j, k] = i+rank*(nx-1)//size + j*nx + k*nx*ny
            
# wrap fields
p  = p.reshape((p.size//p.shape[0],  p.shape[0]), order='F')
fields = {"Pressure": p}
pvtu(pvtuName, relativePath, master, rank, size, 
     vtuName, xyz, cells, cellTypes, **fields)