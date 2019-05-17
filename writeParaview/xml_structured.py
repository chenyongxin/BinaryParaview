"""
Write Paraview XML structured grid file (.vts) in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vts(fname, x, y, z, ise, jse, kse, **kwargs):
    """
    Write structured grid .vts file in binary

    Parameters
    ==========
    fname: string
        file name (without '.vts' extension)

    x,y,z: array-like, float, (nx,ny,nz)
        x,y,z grid point array.

    ise,jse,kse: array-like, int, (2,)
        Vector spcifies the starting and ending indices of Piece's extent.

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

    # write file title
    with open(fname+".vts", 'wb') as fh:
        fh.write(encode('<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode(f'  <StructuredGrid WholeExtent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode(f'    <Piece Extent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode('      <Points>\n'))
        fh.write(encode('        <DataArray type="Float32" Name="Points" format="appended" offset="0" NumberOfComponents="3"/>\n'))
        fh.write(encode('      </Points>\n'))

        #####
        # Additional header of scalar fields or/and vector field if kwargs is present
        if len(kwargs) > 0:
            off = nx*ny*nz*3*4 + 4            # reserved for grid
            fh.write(encode('      <PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode('        <DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'
                                 .format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('      </PointData>\n'))
        #####

        fh.write(encode('    </Piece>\n'))
        fh.write(encode('  </StructuredGrid>\n'))
        fh.write(encode('  <AppendedData encoding="raw">\n'))
        fh.write(encode('_'))
        fh.write(pack("i", 4*nx*ny*nz*3))
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    fh.write(pack("f", x[i,j,k]))
                    fh.write(pack("f", y[i,j,k]))
                    fh.write(pack("f", z[i,j,k]))

        #####
        # Additional data of scalar fields or/and vector field if kwargs is present
        if len(kwargs) > 0:
            for value in kwargs.values():
                fh.write(pack("i", 4*value.size))
                fh.write(pack("f"*value.size, *(value.flatten(order='F'))))
        #####

        fh.write(encode('\n'))
        fh.write(encode('  </AppendedData>\n'))
        fh.write(encode('</VTKFile>\n'))
        
        
def pvts(pvtsName, relativePath, master, nprocs, coords, wise, wjse, wkse, piecesExtent, 
         vtsName, x, y, z, ise, jse, kse, **kwargs):
    """
    Write parallel structured grid .pvtr file and serial .vtr files

    Parameters
    ==========
    pvtsName: string
        File name (without '.pvts' extension)
        
    relativePath: string
        Relative path from .pvts to .vts.
        e.g.
        pvtsName: "a/b/"
        vtsName: "a/b/c/Fluid"
        relativePath: "c/Fluid"

    master: boolean
        Master processor to write .pvtr file.

    nprocs: array-like, int, (3,)
        Number of processors in 3 dimensions.

    coords: array-like, int, (3,)
        MPI topology coordinates. Index starts from 0 as usual.

    wise,wjse,wkse: array-like, int, (2,)
        Vector spcifies the starting and ending indices of WholePiece's extent.

    piecesExtent: array-like, int, (N,6)
        piecesExtent specifies each piece's extent.
        Note:
            N = product(nprocs).
            piecesExtent[MPI-ID, :] = [ise[0], ise[1], jse[0], jse[1], kse[0], kse[1]]

    vtsName: string
        File name (without '.vts' extension).
        Note: vtrName is forename and it is identical for all serial files. The uniqueness of
              each file will be stated by its MPI topology coordinate.
        e.g:
        >>> vtsName = "path/to/vts/example"     # general name as input
        >>> vtsName += ".x1x2x3"                # specific name with coordinate

    x,y,z: array-like, (N,)
        Local x,y,z grid point.

    ise,jse,kse: array-like (2,)
        2-element integer vector spcifies the starting and ending indices of each Piece's extent.

    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz)).
    """
    # write .vts serial file
    vts(vtsName+".x{}x{}x{}".format(*coords), x, y, z, ise, jse, kse, **kwargs)
    
    # write .pvts file
    if master:
        with open(pvtsName+".pvts", 'w') as fh:
            fh.write('<VTKFile type="PStructuredGrid" version="0.1" byte_order="LittleEndian">\n')
            fh.write(f'  <PStructuredGrid WholeExtent="{wise[0]} {wise[1]} {wjse[0]} {wjse[1]} {wkse[0]} {wkse[1]}"\n')
            fh.write('                    GhostLevel="0">\n')
            fh.write('    <PPoints>\n')
            fh.write('      <DataArray type="Float32" Name="Points" NumberOfComponents="3"/>\n')
            fh.write('    </PPoints>\n')
            # write dummy data frame if present
            if len(kwargs) > 0:
                fh.write('    <PPointData>\n')
                for key, value in kwargs.items():
                    ndim = value.shape[0]
                    fh.write('      <DataArray type="Float32" Name="{}" NumberOfComponents="{}"/>\n'
                                     .format(key, ndim))
                fh.write('    </PPointData>\n')
            # write each piece
            n1, n2, n3 = nprocs[0], nprocs[1], nprocs[2]
            for k in range(n3):
                for j in range(n2):
                    for i in range(n1):
                        idx = i + j*n1 + k*n1*n2
                        sourceName = relativePath + ".x{}x{}x{}.vts".format( i,j,k )
                        fh.write('    <Piece Extent="{} {} {} {} {} {}" '.format( *piecesExtent[idx,:] ))
                        fh.write('Source="{}"/>\n'.format(sourceName))
            fh.write('  </PStructuredGrid>\n')
            fh.write('</VTKFile>')