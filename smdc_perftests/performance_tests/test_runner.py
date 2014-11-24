# Copyright (c) 2013,Vienna University of Technology,
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
This module contains functions that
run tests according to specifications from SMDC Performance comparison
document.

Interfaces to data should be interchangeable as long as they adhere
to interface specifications from rsdata module

Created on Tue Oct 21 13:37:58 2014

@author: christoph.paulik@geo.tuwien.ac.at
'''
import time
import random
import numpy as np
from scipy.stats import t

import netCDF4


class TestResults(object):

    """
    Simple object that contains the test results
    and can be used to compare the test results
    to other test results.

    Objects of this type can also be plotted by
    the plotting routines.
    Parameters
    ----------
    measured times or filename: list or string
        list of measured times or netCDF4 file produced
        by to_nc of another TestResults object
    ddof: int
        difference degrees of freedom. This is used to calculate
        standard deviation and variance. It is the number that is
        subtracted from the sample number n when estimating
        the population standard deviation and variance.
        see bessel's correction on e.g. wikipedia for explanation


    Attributes
    ----------
    median: float
        median of the measurements
    n: int
        sample size
    stdev: float
        standard deviation
    var: float
        variance
    total: float
        total time expired
    mean: float
        mean time per test run
    """

    def __init__(self, init_obj,
                 ddof=1):

        if type(init_obj) == str:
            self._from_nc(init_obj)
        elif type(init_obj) == list:
            self._measurements = init_obj

        self.ddof = ddof
        self._init_metrics()

    def _init_metrics(self):
        """
        Initialize the metrics
        """
        self.median = np.median(self._measurements)
        self.n = len(self._measurements)
        self.var = np.var(self._measurements, ddof=self.ddof)
        self.stdev = np.sqrt(self.var)
        self.total = sum(self._measurements)
        self.mean = np.mean(self._measurements)

    def confidence_int(self, conf_level=95):
        """
        Calculate confidence interval of the mean
        time measured

        Parameters
        ----------
        conf_level: float
            confidence level desired for the confidence interval in percent.
            this will be transformed into the quantile needed to get the z value
            for the t distribution.
            default is 95% confidence interval

        Returns
        -------
        lower_mean : float
            lower confidence interval boundary
        mean : float
            mean value
        upper_mean : float
            upper confidence interval boundary

        """
        # calculate quantile from confidence level in percent
        t_quantile = 1 - (1 - conf_level / 100.0) / 2.0
        # get t value from distribution
        t_val = t.ppf(t_quantile, self.n - self.ddof)
        # calculate standard error for estimated values
        std_err = self.stdev / np.sqrt(self.n)
        lower_mean = self.mean - t_val * std_err
        upper_mean = self.mean + t_val * std_err
        return lower_mean, self.mean, upper_mean

    def to_nc(self, filename):
        """
        store results on disk as a netCDF4 file

        Parameters
        ----------
        filename: string
            path and filename
        """
        with netCDF4.Dataset(filename, mode='w') as ncdata:
            ncdata.createDimension('measurements', len(self._measurements))
            msmts = ncdata.createVariable(
                'measurements', 'f8', ('measurements',))
            msmts[:] = self._measurements

    def _from_nc(self, filename):
        """
        initializes object from netCDF4 file
        """
        with netCDF4.Dataset("test.nc") as ncdata:
            self._measurements = ncdata.variables['measurements'][:].tolist()

    def __lt__(self, other):
        """
        Check for overlap of confidence intervals
        only True if upper confidence interval boundary
        is less than lower confidence interval boundary
        of other object
        """
        lms, ms, ums = self.confidence_int()
        lmo, mo, umo = other.confidence_int()
        if ums < lmo:
            return True
        else:
            return False

    def __gt__(self, other):
        """
        Check for overlap of confidence intervals
        only True if lower confidence interval boundary
        is greater than upper confidence interval boundary
        of other object
        """
        lms, ms, ums = self.confidence_int()
        lmo, mo, umo = other.confidence_int()
        if lms > umo:
            return True
        else:
            return False


def measure(runs=5, ddof=1):
    """
    Decorator that measures the running time of a function
    and calculates statistics.

    Parameters
    ----------
    runs: int
        number of test runs to perform
    ddof: int
        difference degrees of freedom. This is used to calculate
        standard deviation and variance. It is the number that is
        subtracted from the sample number n when estimating
        the population standard deviation and variance.
        see bessel's correction on e.g. wikipedia for explanation

    Returns
    =======
    results: dict
        dictionary of the measurement results.
    """
    def decorator(func):
        def inner(*args, **kwargs):
            print "measuring time"
            measured_times = []
            for i in xrange(runs):
                start = time.time()
                func(*args, **kwargs)
                end = time.time()
                duration = end - start
                measured_times.append(duration)
                print duration
            print "measured time now calculating results"
            results = TestResults(measured_times, ddof=ddof)
            return results

        return inner
    return decorator


def read_rand_ts_by_gpi_list(dataset, gpi_list, read_perc=20.0, **kwargs):
    """
    reads time series data for random grid point indices in a list
    additional kwargs are given to read_ts method of dataset

    Parameters
    ----------
    dataset: instance
        instance of a class that implements a read_ts(gpi)
        method
    gpi_list: iterable
        list or numpy array of grid point indices
    read_perc: float
        percentage of points from gpi_list to read

    """
    gpi_read = random.sample(gpi_list, int(len(gpi_list) / read_perc / 100.0))
    for gpi in gpi_read:
        data = dataset.read_ts(gpi, **kwargs)


def read_rand_img_by_date_list(dataset, date_list, read_perc=20.0, **kwargs):
    """
    reads image data for random dates on a list
    additional kwargs are given to read_img method
    of dataset

    Parameters
    ----------
    dataset: instance
        instance of a class that implements a read_img(datetime)
        method
    date_list: iterable
        list of datetime objects
    read_perc: float
        percentage of datetimes out of date_list to read

    """
    date_read = random.sample(
        date_list, int(len(date_list) / read_perc / 100.0))
    for d in date_read:
        data = dataset.read_img(d, **kwargs)