"""
Write Paraview legacy structured grid file in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vts(fname, x, y, z, **kwargs):
    """ Write legacy rectilinear grid file in binary

    Parameters
    ==========
    fname: string
        file name (without '.vtk' extension)

    x,y,z: array-like, float, (nx,ny,nz)
        x,y,z grid point array.

    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz))
    """
    # write bindary data
    from struct import pack
    import numpy as np

    # A encoded string which can be written to binary file
    def encode(string): return str.encode(string)

    # get domain size
    nx,ny,nz = np.shape(x)

    with open(fname+".vtk", 'wb') as fh:
        fh.write(encode("# vtk DataFile Version 2.0\n"))
        fh.write(encode("Visulaization output file\n"))
        fh.write(encode("BINARY\n"))
        fh.write(encode("DATASET STRUCTURED_GRID\n"))
        fh.write(encode("DIMENSIONS {} {} {}\n".format(nx, ny, nz)))
        fh.write(encode("POINTS {} float\n".format(x.size)))
        # make xyz and write it
        xyz = np.stack([x,y,z], axis=0).flatten(order='F')
        fh.write(pack(">"+"f"*x.size*3, *xyz))
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
