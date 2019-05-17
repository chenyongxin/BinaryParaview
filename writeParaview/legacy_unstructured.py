"""
Write Paraview legacy unstructured grid file in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vtu(fname, xyz, cells, cellTypes, **kwargs):
    """ Write unstrcutred grid .vtu file in binary
    Parameters
    ==========
    fname: string
        file name (without '.vtk' extension)

    xyz: numpy array, 2D: n*3
        point coordinates.
        [[x0,      y0,      z0     ],
         ...
         [x_{n-1}, y_{n-1}, z_{n-1}]]

    cells: numpy array, integer
        Defines the connectivity.
        2D array with dimension n*m, where n is the number of cells and m is
        the maximum number of connection of points among all the cells.

    cellTypes: number array, 1D, integer
        Defines cell type of each cell.

    **kwargs: dict, optional
        vector or scalar field.
        Key: field's name.
        Value: numpy array, where 2D array is a scalar field, while 3D array is a vecotr field.
        The field in Value should be arranged as a[n, NumberOfComponents].
    """
    # write bindary data
    from struct import pack

    import numpy as np

    # A encoded string which can be written to binary file
    def encode(string): return str.encode(string)

    # get numbers
    nPoints = xyz.shape[0]
    nCells  = cells.shape[0]

    with open(fname+".vtk", 'wb') as fh:
        fh.write(encode("# vtk DataFile Version 2.0\n"))
        fh.write(encode("Visulaization output file\n"))
        fh.write(encode("BINARY\n"))
        fh.write(encode("DATASET UNSTRUCTURED_GRID\n"))
        fh.write(encode("POINTS {} float\n".format(nPoints)))
        fh.write(pack(">"+"f"*3*nPoints, *(xyz.flatten(order='C'))))
        fh.write(encode("\n"))
        fh.write(encode("CELLS {} {}\n".format(nCells, nCells+np.sum(cells[:,0]))))
        for i,n in enumerate(cells[:,0]): fh.write(pack(">"+"i"*(n+1), *(cells[i,:n+1])))
        fh.write(encode("\n"))
        fh.write(encode("CELL_TYPES {}\n".format(cellTypes.size)))
        fh.write(pack(">"+"i"*nCells, *cellTypes))
        fh.write(encode("\n"))
        # write data if kwargs is present
        if len(kwargs) > 0:
            fh.write(encode("POINT_DATA {}\n".format(nPoints)))
            for key, value in kwargs.items():
                ndim = value.shape[1]
                fh.write(encode("SCALARS {} float {}\n".format(key, ndim)))
                fh.write(encode("LOOKUP_TABLE default\n"))
                fh.write( pack(">"+"f"*value.size, *(value.flatten(order='F'))) )
                fh.write(encode("\n"))
