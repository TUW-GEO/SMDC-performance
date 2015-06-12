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
import pandas as pd
import os
import pygeogrids.grids as grids
from datetime import timedelta


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
            lsmaskfile = os.path.join(os.path.dirname(__file__), "..", "bin",
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


class ASCAT_netcdf(object):

    """
    Class for reading ASCAT data from netCDF files

    Caches the following:
    - time variable
    - keeps the dataset open as long as the instance exists

    """

    def __init__(self, fname, variables=None, avg_var=None, time_var='time',
                 gpi_var='gpis_correct', cell_var='cells_correct',
                 get_exact_time=False):
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
        gpi_var: string, optional
            name of the gpi variable in the netCDF file
        cell_var: string, optional
            name of the cell variable in the netCDF file
        get_exact_time: boolean, optional
            for time series deliver the exact time and not the one rounded to the
            next hour.
        """

        self.fname = fname
        self.ds = nc.Dataset(fname)
        self.gpi_var = gpi_var
        self.cell_var = cell_var
        self.time_var = time_var
        self.avg_var = avg_var
        self.get_exact_time = get_exact_time

        if variables is None:
            self.variables = self.ds.variables.keys()
            # exclude time, lat and lon from variable list
            self.variables.remove(self.time_var)
            self.variables.remove(self.gpi_var)
            self.variables.remove(self.cell_var)
            # remove old variables that were added by mistake
            self.variables.remove('cells')
            self.variables.remove('orig_gpis')
            self.variables.remove('row_size')
            self.variables.remove('exact_time')
            self.variables.remove('gpis')
        else:
            self.variables = variables
            # make sure ssf is always there for masking
            if self.avg_var is not None:
                if 'ssf' not in self.variables:
                    self.variables.append('ssf')

        self.gpis = self.ds.variables[self.gpi_var][:]
        self.orig_gpis = self.ds.variables['orig_gpis'][:]
        self.row_size = self.ds.variables['row_size'][:]
        self.exact_time = self.ds.variables['exact_time']
        self.cells = self.ds.variables[self.cell_var][:]
        self.times = nc.num2date(self.ds.variables[self.time_var][:],
                                 units=self.ds.variables[self.time_var].units)
        self._init_grid()

    def _init_grid(self):
        """
        initialize the grid of the dataset
        """
        self.grid = ASCAT_grid()

    def get_timeseries(self, locationid, date_start=None, date_end=None):
        """
        Parameters
        ----------
        locationid: int
            location id as lat_index * row_length + lon_index
        date_start: datetime, optional
            start date of the time series
        date_end: datetime, optional
            end date of the time series

        Returns
        -------
        ts : dict
        """
        start_index, end_index = None, None
        if date_start is not None:
            start_index = nc.netcdftime.date2index(date_start,
                                                   self.ds.variables[self.time_var])
        if date_end is not None:
            end_index = nc.netcdftime.date2index(date_end,
                                                 self.ds.variables[self.time_var])

        date_slice = slice(start_index, end_index, None)
        # get position in netCDF from location id
        pos = np.where(self.gpis == locationid)[0][0]
        ts = {}
        for v in self.variables:
            ts[v] = self.ds.variables[v][date_slice, pos]

        ds = pd.DataFrame(ts, index=self.times)
        if self.get_exact_time:
            # read exact time values for gpi and
            ds = ds.dropna(how='all')
            pos = np.where(self.orig_gpis == locationid)[0][0]
            start_etime = np.sum(self.row_size[:pos])
            end_etime = np.sum(self.row_size[:pos + 1])
            exact_time = nc.num2date(self.exact_time[start_etime:end_etime],
                                     self.exact_time.units)
            et = pd.DataFrame({'date': exact_time}, index=exact_time)
            et = et.resample("H", how='first')
            ds = ds.join(et).dropna().set_index('date')

        return ds

    def get_avg_image(self, date_start, date_end=None, cellID=None):
        """
        Reads image from dataset, takes the average if more than one value is in the result array.

        Parameters
        ----------
        date_start: datetime
            start date of the image to get. If only one date is given then
            the whole day of this date is read
        date_end: datetime, optional
            end date of the averaged image to get
        cellID: int, optional
            cell id to which the image should be limited, for ESA CCI this is
            not defined at the moment.
        """
        if date_end is None:
            date_end = date_start + timedelta(days=1)
        img = self.get_data(date_start, date_end, cellID=cellID)
        # calculate average
        for v in img:
            if self.avg_var is not None:
                if v in self.avg_var:
                    img[v][img['ssf'] != 1] = np.nan
                    img[v] = np.nanmean(img[v], axis=0)
        return img

    def get_data(self, date_start, date_end, cellID=None):
        """
        Reads date cube from dataset

        Parameters
        ----------
        date_start: datetime
            start date of the image to get. If only one date is given then
            the whole day of this date is read
        date_end: datetime
            end date of the averaged image to get
        cellID: int
            cell id to which the image should be limited, for ESA CCI this is
            not defined at the moment.
        """
        start_index = nc.netcdftime.date2index(date_start,
                                               self.ds.variables[self.time_var])
        end_index = nc.netcdftime.date2index(date_end,
                                             self.ds.variables[self.time_var])
        date_slice = slice(start_index, end_index + 1, None)

        gpi_slice = slice(None, None, None)
        if cellID is not None:
            cell_pos = np.where(self.cells == cellID)[0]
            gpi_slice = slice(cell_pos[0], cell_pos[-1] + 1, None)

        img = {}
        for v in self.variables:
            if v in ['ssm', 'ssm_noise']:
                img[v] = self.ds.variables[v][
                    date_slice, gpi_slice].astype(np.float)
            else:
                img[v] = self.ds.variables[v][date_slice, gpi_slice]

        return img
