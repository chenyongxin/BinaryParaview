"""
Example code:
Write legacy rectilinear grid in 3D.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.legacy_rectilinear import vtr
import numpy as np
import os

# make output folder
if not os.path.isdir("output"): os.mkdir("output")

nx, ny, nz = 101, 51, 61
x = np.linspace(0, nx-1, nx)
y = np.linspace(0, ny-1, ny)
z = np.linspace(0, nz-1, nz)

p = np.zeros((1, nx, ny, nz))
v = np.zeros((3, nx, ny, nz))

for j in range(p.shape[2]):
    p[:,:,j,:] = j

for i in range(v.shape[1]):
    v[0,i,:,:] = i
for j in range(v.shape[2]):
    v[1,:,j,:] = j
for k in range(v.shape[3]):
    v[2,:,:,k] = k

fields = {"Pressure":p, "Velocity":v}
vtr("output/Legacy_rectilinear", x, y, z, **fields)