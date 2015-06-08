# Copyright (c) 2015,Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Vienna University of Technology,
#      Department of Geodesy and Geoinformation nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

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
Dataset Reader for EQUI-7 data
Created on Mon Jun  8 17:30:19 2015

'''
import netCDF4 as nc
import numpy as np

from smdc_perftests.datasets.esa_cci import ESACCI_netcdf
import pygeogrids.grids as grids


class EQUI_7(ESACCI_netcdf):

    def __init__(self, fname, variables=None, avg_var=None, time_var='time', lat_var='x', lon_var='y'):
        """
        Parameters
        ----------
        self: type
            description
        fname: string
            filename
        variables: list, optional
            if given only these variables will be read
        avg_var: list, optional
            list of variables for which to calculate the average if not given
            it is calculated for all variables
        time_var: string, optional
            name of the time variable in the netCDF file
        lat_var: string, optional
            name of the latitude variable in the netCDF file
        lon_var: string, optional
            name of the longitude variable in the netCDF file
        """

        self.fname = fname
        self.ds = nc.Dataset(fname)
        self.lat_var = lat_var
        self.lon_var = lon_var
        self.time_var = time_var
        self.avg_var = avg_var

        if variables is None:
            self.variables = self.ds.variables.keys()
            # exclude time, lat and lon from variable list
            self.variables.remove(self.time_var)
            self.variables.remove(self.lat_var)
            self.variables.remove(self.lon_var)
        else:
            self.variables = variables

        self._init_grid()

    def _init_grid(self):
        """
        initialize the grid of the dataset
        """
        x = self.ds.variables[self.lat_var][:]
        y = self.ds.variables[self.lon_var][:]
        xs, ys = np.meshgrid(x, y)
        self.grid = grids.BasicGrid(
            xs.flatten(), ys.flatten(), shape=(1200, 2400))
