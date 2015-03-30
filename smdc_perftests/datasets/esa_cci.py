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
Module contains the Class for reading ESA CCI data in netCDF Format
Created on Fri Mar 27 15:12:18 2015

@author: Christoph.Paulik@geo.tuwien.ac.at
'''

import netCDF4 as nc
import numpy as np
import pytesmo.grid.grids as grids


class ESACCI(object):

    """
    Class for reading ESA CCI data

    Caches the following:
    - time variable
    - keeps the dataset open as long as the instance exists

    """

    def __init__(self, fname, variables=None, time_var='time'):
        """
        Parameters
        ----------
        self: type
            description
        fname: string
            filename
        variables: list, optional
            if given only these variables will be read
        time_var: string, optional
            name of the time variable in the netCDF file
        """

        self.fname = fname
        self.ds = nc.Dataset(fname)
        if variables is None:
            self.variables = self.ds.variables.keys()
        else:
            self.variables = variables

        self.time_var = time_var
        self.init_grid()

    def init_grid(self):
        """
        initialize the grid of the dataset
        """
        latgrid, longrid = np.meshgrid(self.ds.variables['lon'][:],
                                       self.ds.variables['lat'][:])
        self.grid = grids.BasicGrid(longrid.flatten(), latgrid.flatten(),
                                    shape=(720, 1440))

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
        # get row, column from location id
        row, col = self.grid.gpi2rowcol(locationid)
        ts = {}
        for v in self.variables:
            ts[v] = self.ds.variables[v][date_slice, row, col]
        return ts

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
        start_index = nc.netcdftime.date2index(date_start,
                                               self.ds.variables[self.time_var])
        if date_end is None:
            date_end = date_start
        img = self.get_data(date_start, date_end)
        # calculate average
        for v in img:
            img[v] = img[v].mean(axis=0)

    def get_data(self, date_start, date_end, cellID=1):
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
        date_slice = slice(start_index, end_index, None)

        img = {}
        for v in self.variables:
            img[v] = self.ds.variables[v][date_slice, :, :]

        return img
