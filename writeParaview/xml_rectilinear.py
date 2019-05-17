"""
Write Paraview XML serial and parallel rectilinear grid file (.vtr and .pvtr) in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vtr(fname, x, y, z, ise, jse, kse, **kwargs):
    """
    Write serial rectilinear grid .vtr file in binary

    Parameters
    ==========
    fname: string
        file name (without '.vtr' extension)

    x,y,z: array-like, float, (N,)
        x,y,z grid point.

    ise,jse,kse: array-like, int, (2,)
        Vector spcifies the starting and ending indices of Piece's extent.

    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz))
    """
    # write bindary data
    from struct import pack

    # A encoded string which can be written to binary file
    def encode(string): return str.encode(string)

    # get domain size (local)
    nx, ny, nz = x.size, y.size, z.size

    # init offset
    off = 0

    # write file title
    with open(fname+".vtr", 'wb') as fh:
        fh.write(encode('<VTKFile type="RectilinearGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode(f'  <RectilinearGrid WholeExtent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode(f'    <Piece Extent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode('      <Coordinates>\n'))
        fh.write(encode(f'        <DataArray type="Float32" Name="x" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nx*4 + 4
        fh.write(encode(f'        <DataArray type="Float32" Name="y" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += ny*4 + 4
        fh.write(encode(f'        <DataArray type="Float32" Name="z" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nz*4 + 4
        fh.write(encode('      </Coordinates>\n'))

        #####
        # Additional header of scalar fields or/and vector field if kwargs is present
        if len(kwargs) > 0:
            fh.write(encode('      <PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode('        <DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'
                                 .format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('      </PointData>\n'))
        #####

        fh.write(encode('    </Piece>\n'))
        fh.write(encode('  </RectilinearGrid>\n'))
        fh.write(encode('  <AppendedData encoding="raw">\n'))
        fh.write(encode('_'))
        fh.write(pack("i",   4*nx))
        fh.write(pack("f"*nx,  *x))
        fh.write(pack("i",   4*ny))
        fh.write(pack("f"*ny,  *y))
        fh.write(pack("i",   4*nz))
        fh.write(pack("f"*nz,  *z))

        #####
        # Additional data of scalar fields or/and vector field if kwargs is present
        if len(kwargs) > 0:
            for value in kwargs.values():
                fh.write(pack("i", 4*value.size))
                fh.write(pack("f"*value.size, *(value.flatten(order='F'))))
        #####

        fh.write(encode('  </AppendedData>\n'))
        fh.write(encode('</VTKFile>\n'))

def pvtr(pvtrName, relativePath, master, nprocs, coords, wise, wjse, wkse, piecesExtent, 
        vtrName, x, y, z, ise, jse, kse, **kwargs):
    """
    Write parallel rectilinear grid .pvtr file and serial .vtr files

    Parameters
    ==========
    pvtrName: string
        File name (without '.pvtr' extension)
        
    relativePath: string
        Relative path from .pvtr to .vtr.
        e.g.
        pvtrName: "a/b/"
        vtrName: "a/b/c/Fluid"
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

    vtrName: string
        File name (without '.vtr' extension).
        Note: vtrName is forename and it is identical for all serial files. The uniqueness of
              each file will be stated by its MPI topology coordinate.
        e.g:
        >>> vtrName = "path/to/vtr/example"     # general name as input
        >>> vtrName += ".x1x2x3"                # specific name with coordinate

    x,y,z: array-like, (N,)
        Local x,y,z grid point.

    ise,jse,kse: array-like (2,)
        2-element integer vector spcifies the starting and ending indices of each Piece's extent.

    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz)).
    """
    # write .vtr serial File
    vtr(vtrName+".x{}x{}x{}".format(*coords), x, y, z, ise, jse, kse, **kwargs)

    # write .pvtr file
    if master:
        with open(pvtrName+".pvtr", 'w') as fh:
            fh.write('<VTKFile type="PRectilinearGrid" version="0.1" byte_order="LittleEndian">\n')
            fh.write(f'  <PRectilinearGrid WholeExtent="{wise[0]} {wise[1]} {wjse[0]} {wjse[1]} {wkse[0]} {wkse[1]}"\n')
            fh.write('                    GhostLevel="0">\n')
            fh.write('    <PCoordinates>\n')
            fh.write('      <DataArray type="Float32" Name="x"/>\n')
            fh.write('      <DataArray type="Float32" Name="y"/>\n')
            fh.write('      <DataArray type="Float32" Name="z"/>\n')
            fh.write('    </PCoordinates>\n')
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
                        sourceName = relativePath + ".x{}x{}x{}.vtr".format( i,j,k )
                        fh.write('    <Piece Extent="{} {} {} {} {} {}" '.format( *piecesExtent[idx,:] ))
                        fh.write('Source="{}"/>\n'.format(sourceName))
            fh.write('  </PRectilinearGrid>\n')
            fh.write('</VTKFile>')
