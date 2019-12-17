"""
Example code:
Write parallel XML structured grid in 3D.

Only 1D decomposision is used. 

To execuate this code, run command in terminal (Linux/Mac) or cmd (Windows):
mpiexec -n 3 python Parallel_XML_structured.py

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.xml_structured import pvts
from grid.MakeGrid import MakeGrid
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
pvtsDir = "output/"         # path to save .pvts file
vtsDir  = "output/data/"    # path to save .vts files
relativeDir =    "data/"    # relative path from .pvts to .vts
pvtsName = pvtsDir + "Parallel_XML_structured" 
pieceName = "Seial_XML_structured_Piece"
vtsName = vtsDir + pieceName                    
relativePath = relativeDir + pieceName

# make output folder
if master:
    if not os.path.isdir(pvtsDir): os.mkdir(pvtsDir)
    if not os.path.isdir(vtsDir): os.mkdir(vtsDir)
    
# Make global grid
# 2D grid
nx = 120
ny = 60
x, y = MakeGrid(nx+1, ny+1)

# 3rd dimension
nz =  20
dz = .25

# extrude
x = np.stack([x for _ in range(nz+1)], axis=-1)
y = np.stack([y for _ in range(nz+1)], axis=-1)
z = np.stack([np.zeros((nx+1, ny+1))+i*dz for i in range(nz+1)], axis=-1)

# global quantities
nprocs = [size, 1, 1]                  # number of processors in 3 dimensions
wise = np.array([1, nx+1]) - 1         # WholeExtent, with 0 start
wjse = np.array([1, ny+1]) - 1
wkse = np.array([1, nz+1]) - 1

# local quantities
pnx, pny, pnz = nx//size, ny, nz       # number of points in this partition
coords = [rank, 0, 0]                  # MPI coordinate
xlocal = x.copy()[ nx//size*rank : nx//size*(rank+1)+1, :, : ]
ylocal = y.copy()[ nx//size*rank : nx//size*(rank+1)+1, :, : ]
zlocal = z.copy()[ nx//size*rank : nx//size*(rank+1)+1, :, : ]

# local piece starting/ending indices
ise = np.array([ nx//size*rank, nx//size*(rank+1) ])
jse = wjse.copy()
kse = wkse.copy()
piecesExtent = np.zeros((size, 6), dtype=int)

# for .pvts file
for i in range(size):
    piecesExtent[i, :] = [nx//size*i, nx//size*(i+1), jse[0], jse[1], kse[0], kse[1]]

# make a local scalar field
p = np.zeros((1, pnx+1, pny+1, pnz+1))
for k in range(pnz+1):
    for j in range(pny+1):
        for i in range(pnx+1):
            p[:, i, j, k] = i+rank*pnx + j*(nx+1) + k*(nx+1)*(ny+1)
            
# wrap fields
fields = {"Pressure": p}

# all done, write .pvts file and .vts files
pvts(pvtsName, relativePath, master, nprocs, coords, wise, wjse, wkse, piecesExtent, 
     vtsName, xlocal, ylocal, zlocal, ise, jse, kse, **fields)
