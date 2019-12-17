"""
Example code:
Write parallel XML rectillinear grid in 3D.

Only 1D decomposision is used.

To execuate this code, run command in terminal (Linux/Mac) or cmd (Windows):
mpiexec -n 3 python Parallel_XML_rectilinear.py

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.xml_rectilinear import pvtr
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
pvtrDir = "output/"         # path to save .pvtr file
vtrDir  = "output/data/"    # path to save .vtr files
relativeDir =    "data/"    # relative path from .pvtr to .vtr
pvtrName = pvtrDir + "Parallel_XML_rectilinear" 
pieceName = "Seial_XML_rectilinear_Piece"
vtrName = vtrDir + pieceName                    
relativePath = relativeDir + pieceName

# make output folder
if master:
    if not os.path.isdir(pvtrDir): os.mkdir(pvtrDir)
    if not os.path.isdir(vtrDir): os.mkdir(vtrDir)

# global quantities
nx, ny, nz = 121, 31, 31               # number of points
ncx, ncy, ncz = nx-1, ny-1, nz-1       # number of cells
x = np.linspace(1, ncx+1, ncx+1) - 1   # global coordinates, 
y = np.linspace(1, ncy+1, ncy+1) - 1   
z = np.linspace(1, ncz+1, ncz+1) - 1  
nprocs = [size, 1, 1]                  # number of processors in 3 dimensions
wise = np.array([1, nx]) - 1           # WholeExtent, with 0 start
wjse = np.array([1, ny]) - 1
wkse = np.array([1, nz]) - 1

# local quantities
pnx, pny, pnz = ncx//size+1, ny, nz    # number of points in this partition
coords = [rank, 0, 0]                  # MPI coordinate
xlocal = x.copy()[ ncx//size*rank : ncx//size*(rank+1)+1 ]
ylocal = y.copy()
zlocal = z.copy()

# local piece starting/ending indices
ise = np.array([ ncx//size*rank, ncx//size*(rank+1) ])
jse = wjse.copy()
kse = wkse.copy()
piecesExtent = np.zeros((size, 6), dtype=int)

# for .pvtr file
for i in range(size):
    piecesExtent[i, :] = [ncx//size*i, ncx//size*(i+1), jse[0], jse[1], kse[0], kse[1]]

# make a scalar field
p = np.zeros((1, pnx, pny, pnz))
# assign interior region of local field
for k in range(pnz):
    for j in range(pny):
        for i in range(pnx):
            p[:, i, j, k] = i+rank*(pnx-1) + j*nx + k*nx*ny

# wrap fields
fields = {"Pressure": p}

# all done, write .pvtr file and .vtr files
pvtr(pvtrName, relativePath, master, nprocs, coords, wise, wjse, wkse, piecesExtent, 
         vtrName, xlocal, ylocal, zlocal, ise, jse, kse, **fields)
