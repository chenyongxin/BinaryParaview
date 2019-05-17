"""
Example code:
Write serial XML structured grid in 2D.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

from writeParaview.xml_structured import vts
from grid.MakeGrid import MakeGrid
import numpy as np
import os

# make output folder
if not os.path.isdir("output"): os.mkdir("output")

# 2D grid
x, y = MakeGrid()

# convert 2D to 3D
x = x.reshape(x.shape+(1,))
y = y.reshape(y.shape+(1,))
z = np.zeros_like(x)

# make scalar field p, 2-component field, 3-component field
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

v3[2,:,:,:] = 5

fields = {"Pressure":p, "V2":v2, "V3":v3}
ise = np.array([1,x.shape[0]], dtype=int)
jse = np.array([1,x.shape[1]], dtype=int)
kse = np.array([1,x.shape[2]], dtype=int)

vts("output/Serial_XML_structured2D", x, y, z, ise, jse, kse, **fields)