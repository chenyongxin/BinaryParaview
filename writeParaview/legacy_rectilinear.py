"""
Write Paraview legacy rectilinear grid file in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vtr(fname, x, y, z, **kwargs):
    """ Write legacy rectilinear grid file in binary

    Parameters
    ==========
    fname: string
        file name (without '.vtk' extension)

    x,y,z: array-like, float, (N,)
        x,y,z grid point.

    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz))
    """
    # write bindary data
    from struct import pack

    # A encoded string which can be written to binary file
    def encode(string): return str.encode(string)

    # get domain size
    nx, ny, nz = x.size, y.size, z.size

    # write file title
    with open(fname+".vtk", 'wb') as fh:
        fh.write(encode("# vtk DataFile Version 2.0\n"))
        fh.write(encode("Visulaization output file\n"))
        fh.write(encode("BINARY\n"))
        fh.write(encode("DATASET RECTILINEAR_GRID\n"))
        fh.write(encode("DIMENSIONS {} {} {}\n".format(nx, ny, nz)))

        # write coordinates
        # x
        fh.write(encode("X_COORDINATES  {} float\n".format(nx)))
        fh.write(pack(">"+"f"*nx, *x))
        fh.write(encode("\n"))
        # y
        fh.write(encode("Y_COORDINATES  {} float\n".format(ny)))
        fh.write(pack(">"+"f"*ny, *y))
        fh.write(encode("\n"))
        # z
        fh.write(encode("Z_COORDINATES  {} float\n".format(nz)))
        fh.write(pack(">"+"f"*nz, *z))
        fh.write(encode("\n"))

        # write data if kwargs is present
        if len(kwargs) > 0:
            fh.write(encode("POINT_DATA {}\n".format(nx*ny*nz)))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode("SCALARS {} float {}\n".format(key, ndim)))
                fh.write(encode("LOOKUP_TABLE default\n"))
                fh.write( pack(">"+"f"*value.size, *value.flatten(order='F')) )
                fh.write(encode("\n"))
