"""
Make 2D grid.

@author: CHEN Yongxin
@organization: University of Southampton
@contact: y.chen@soton.ac.uk
"""

def MakeGrid(nx=121, ny=61):
    """ Make structured mesh of a half circular ring

    Parameters
    ==========
    nx, ny: int, optional
        number of grid points in tangential and radial directions.

    Returns
    =======
    x,y: array-like
        coordinates of x and y points.
    """
    import numpy as np

    R1, R2 = 5., 10.            # radiuses of interior and exterior arcs.

    x = np.zeros((nx, ny))      # grid coordinate
    y = np.zeros((nx, ny))

    dr = (R2-R1)/(ny-1)
    dtheta = np.pi/(nx-1)

    for j in range(ny):
        r = R1 + dr*j
        for i in range(nx):
            x[i,j] = r*np.cos(i*dtheta)
            y[i,j] = r*np.sin(i*dtheta)

    return x, y


def PlotGrid(x, y):
    """ Plot structured grid

    Parameters
    ==========
    x,y: array-like
        coordinate of x and y points.

    Returns
    =======
    fig: figure object
    """
    import matplotlib.pyplot as plt
    nx, ny = x.shape
    fig = plt.figure()

    # \xi direction
    for j in range(ny):
        plt.plot( x[:,j], y[:,j], 'k' )

    # \eta direction
    for i in range(nx):
        plt.plot( x[i,:], y[i,:], 'k' )

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
    return fig

if __name__ == "__main__":

    # customized parameters
    nx, ny = 31, 21
    plotGrid = True
    savePlot = True

    # get grid mesh
    x, y = MakeGrid(nx,ny)

    # plot grid
    if plotGrid:
        fig = PlotGrid(x, y)
        if savePlot: fig.savefig("Grid.png", dpi=300)
