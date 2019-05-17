"""
Write Paraview XML unstructured grid file (.vtu) in binary.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def vtu(fname, xyz, cells, cellTypes, **kwargs):
    """ Write unstrcutred grid .vtu file in binary
    Parameters
    ==========
    fname: string
        file name (without '.vtu' extension)

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

    # init offset
    off = 0

    # write file title
    with open(fname+".vtu", 'wb') as fh:
        fh.write(encode('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode('  <UnstructuredGrid>\n'))
        fh.write(encode('    <Piece NumberOfPoints="{}" NumberOfCells="{}">\n'.format(nPoints, nCells)))
        fh.write(encode('      <Points>\n'))
        fh.write(encode('        <DataArray type="Float32" Name="Points" format="appended" offset="0" NumberOfComponents="3"/>\n'))
        fh.write(encode('      </Points>\n'))
        fh.write(encode('      <Cells>\n'))
        off += nPoints*3*4 + 4
        fh.write(encode(f'        <DataArray type="Int32" Name="connectivity" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += np.sum(cells[:,0])*4 + 4
        fh.write(encode(f'        <DataArray type="Int32" Name="offsets" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nCells*4 + 4
        fh.write(encode(f'        <DataArray type="Int32" Name="types" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nCells*4 + 4
        fh.write(encode('      </Cells>\n'))

        #####
        # Additional header of scalar fields or/and vector field if kwargs is present
        if len(kwargs) > 0:
            fh.write(encode('      <PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[1]
                fh.write(encode('        <DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'
                                 .format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('      </PointData>\n'))
        #####

        fh.write(encode('    </Piece>\n'))
        fh.write(encode('  </UnstructuredGrid>\n'))
        fh.write(encode('  <AppendedData encoding="raw">\n'))
        fh.write(encode('_'))

        # points
        fh.write(pack("i", 4*nPoints*3))
        for i in range(nPoints):
            fh.write(pack("f"*3, *xyz[i,:]))

        # connectivity
        fh.write(pack("i", 4*np.sum(cells[:,0])))
        for i in range(nCells):
            for j in range(cells[i,0]):
                fh.write(pack("i", cells[i,j+1]))

        # offsets
        fh.write(pack("i", 4*nCells))
        offsets = np.cumsum(cells[:,0])
        for i in range(nCells):
            fh.write(pack("i", offsets[i]))

        # types
        fh.write(pack("i", 4*nCells))
        for i in range(nCells):
            fh.write(pack("i", cellTypes[i]))

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
        
def pvtu(pvtuName, relativePath, master, rank, nprocs,  
         vtuName, xyz, cells, cellTypes, **kwargs):
    """
    Write parallel unstructured grid .pvtu file and serial .vtu files

    Parameters
    ==========
    pvtuName: string
        File name (without '.pvtu' extension)
        
    relativePath: string
        Relative path from .pvtu to .vtu.
        e.g.
        pvtuName: "a/b/"
        vtuName: "a/b/c/Fluid"
        relativePath: "c/Fluid"

    master: boolean
        Master processor to write .pvtr file.

    rank: scalar, int
        Rank of current processor.

    nprocs: scalar, int
        Number of processors.
        
    vtuName: string
        File name (without '.vtu' extension).
        Note: vtuName is forename and it is identical for all serial files. The uniqueness of
              each file will be stated by its MPI rank.
        e.g:
        >>> vtuName = "path/to/vtu/example"    # general name as input
        >>> vtuName += f".x{rank}"             # specific name with coordinate
        
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
    # write .vtu serial file
    vtu(vtuName + f".x{rank}", xyz, cells, cellTypes, **kwargs)
    
    # write .pvtu file
    if master:
        with open(pvtuName+".pvtu", 'w') as fh:
            fh.write('<VTKFile type="PUnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
            fh.write('  <PUnstructuredGrid GhostLevel="0">\n')
            fh.write('    <PPoints>\n')
            fh.write('      <DataArray type="Float32" Name="Points" NumberOfComponents="3"/>\n')
            fh.write('    </PPoints>\n')
            # write dummy data frame if present
            if len(kwargs) > 0:
                fh.write('    <PPointData>\n')
                for key, value in kwargs.items():
                    ndim = value.shape[1]
                    fh.write('      <DataArray type="Float32" Name="{}" NumberOfComponents="{}"/>\n'
                                     .format(key, ndim))
                fh.write('    </PPointData>\n')
            # write each piece
            for i in range(nprocs):
                sourceName = relativePath + f".x{i}.vtu"
                fh.write('    <Piece Source="{}"/>\n'.format(sourceName))
            fh.write('  </PUnstructuredGrid>\n')
            fh.write('</VTKFile>')