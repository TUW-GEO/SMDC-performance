# Copyright (c) 2015,Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Module contains the Classes for reading ASCAT data
Created on Fri Mar 27 15:12:18 2015

@author: Christoph.Paulik@geo.tuwien.ac.at
'''

import netCDF4 as nc
import numpy as np
import os
import pytesmo.grid.grids as grids


class ASCAT_grid(grids.CellGrid):

    """
    ASCAT grid class

    Attributes
    ----------
    land_ind: numpy.ndarray
        indices of the land points
    """

    def __init__(self, lsmaskfile=None):
        if lsmaskfile is None:
            lsmaskfile = os.path.join(os.path.dirname(__file__), "..", "..", "bin",
                                      "ascat",
                                      "TUW_WARP5_grid_info_2_1.nc")
        with nc.Dataset(lsmaskfile) as ls:
            land = ls.variables['land_flag'][:]
            valid_points = np.where(land == 1)[0]

            # read whole grid information because this is faster than reading
            # only the valid points
            lon = ls.variables['lon'][:]
            lat = ls.variables['lat'][:]
            gpis = ls.variables['gpi'][:]
            cells = ls.variables['cell'][:]
            self.land_ind = gpis[valid_points]

        super(ASCAT_grid, self).__init__(lon[valid_points], lat[valid_points],
                                         cells[valid_points],
                                         gpis=gpis[valid_points])
