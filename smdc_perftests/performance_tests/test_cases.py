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
import math

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

    def __init__(self, init_obj, name=None,
                 ddof=1):

        if type(init_obj) == str:
            self._from_nc(init_obj)
        elif type(init_obj) == list:
            self._measurements = init_obj
            if name is None:
                raise ValueError("Name must be given for new results.")
            self.name = name

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

    def __str__(self):
        string = [""]
        string.append("Results %s" % self.name)
        string.append("%d runs" % self.n)
        string.append("median %.4f mean %.4f stdev %.4f" %
                      (self.median, self.mean, self.stdev))
        string.append("sum %.4f" % self.total)
        string.append(
            "95%% confidence interval of the mean")
        conf = self.confidence_int()
        string.append("upper %.4f" % conf[2])
        string.append("       |")
        string.append("mean  %.4f" % conf[1])
        string.append("       |")
        string.append("lower %.4f" % conf[0])
        return '\n'.join(string)

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

            ncdata.setncatts({'dataset_name': self.name})

    def _from_nc(self, filename):
        """
        initializes object from netCDF4 file
        """
        with netCDF4.Dataset(filename) as ncdata:
            self._measurements = ncdata.variables['measurements'][:].tolist()
            self.name = ncdata.dataset_name

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


class SelfTimingDataset(object):

    """
    Dataset class that times the functions of
    a dataset instance it gets in it's constructor

    Stores the results as TestResults instances in a
    dictionary with the timed function names as keys.
    """

    def __init__(self, ds, timefuncs=["get_timeseries",
                                      "get_avg_image",
                                      "get_data"]):
        self.ds = ds
        self.timefuncs = timefuncs
        self.measurements = {}
        # link attributes of this class to attributes of
        # measuring class
        for func in timefuncs:
            self.gentimedfunc(func)
            self.measurements[func] = []

    def gentimedfunc(self, funcname):
        """
        generate a timed function that calls
        the function of the given dataset
        but returns the execution time

        Parameters
        ----------
        funcname: string
            function to create/call of the timed dataset
        """

        def f(*args, **kwargs):
            start = time.time()
            getattr(self.ds, funcname)(*args, **kwargs)
            end = time.time()
            duration = end - start
            self.measurements[funcname].append(duration)

        setattr(self, funcname, f)

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.ds, name)


def measure(exper_name, runs=5, ddof=1):
    """
    Decorator that measures the running time of a function
    and calculates statistics.

    Parameters
    ----------
    exper_name: string
        experiment name, used for plotting and saving
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
        TestResults instance
    """
    def decorator(func):
        def inner(*args, **kwargs):
            measured_times = []
            for i in xrange(runs):
                start = time.time()
                func(*args, **kwargs)
                end = time.time()
                duration = end - start
                measured_times.append(duration)
            results = TestResults(measured_times, exper_name, ddof=ddof)
            return results

        return inner
    return decorator


def read_rand_ts_by_gpi_list(dataset, gpi_list, read_perc=1.0,
                             max_runtime=None, **kwargs):
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
    max_runtime: int, optional
        maximum runtime of test in second.
    **kwargs:
        other keywords are passed to the get_timeseries method
        dataset
    """
    gpi_read = random.sample(
        gpi_list, int(math.ceil(len(gpi_list) * read_perc / 100.0)))
    print "reading {} out of {} time series".format(len(gpi_read), len(gpi_list))

    start = time.time()
    for gpi in gpi_read:
        data = dataset.get_timeseries(int(gpi), **kwargs)
        if max_runtime is not None:
            end = time.time()
            duration = end - start
            if duration > max_runtime:
                break


def read_rand_img_by_date_list(dataset, date_list, read_perc=1.0,
                               max_runtime=None, **kwargs):
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
    max_runtime: int, optional
        maximum runtime of test in second.
    **kwargs:
        other keywords are passed to the get_avg_image method
        dataset
    """
    date_read = random.sample(
        date_list, int(math.ceil(len(date_list) * read_perc / 100.0)))
    print "reading {} out of {} dates".format(len(date_read), len(date_list))

    start = time.time()
    for d in date_read:
        data = dataset.get_avg_image(d, **kwargs)
        if max_runtime is not None:
            end = time.time()
            duration = end - start
            if duration > max_runtime:
                break


def read_rand_img_by_date_range(dataset, date_list, read_perc=1.0,
                                max_runtime=None, **kwargs):
    """
    reads image data between random dates on a list
    additional kwargs are given to read_img method
    of dataset

    Parameters
    ----------
    dataset: instance
        instance of a class that implements a read_img(datetime)
        method
    date_list: iterable
        list of datetime objects
        The format is a list of lists e.g.
        [[datetime(2007,1,1), datetime(2007,1,1)], #reads one day
         [datetime(2007,1,1), datetime(2007,12,31)]] # reads one year
    read_perc: float
        percentage of datetimes out of date_list to read
    max_runtime: int, optional
        maximum runtime of test in second.
    **kwargs:
        other keywords are passed to the get_avg_image method
        dataset
    """
    date_read = random.sample(
        date_list, int(math.ceil(len(date_list) * read_perc / 100.0)))
    print "reading {} out of {} dates".format(len(date_read), len(date_list))

    start = time.time()
    for d1, d2 in date_read:
        data = dataset.get_avg_image(d1, d2, **kwargs)
        if max_runtime is not None:
            end = time.time()
            duration = end - start
            if duration > max_runtime:
                break


def read_rand_cells_by_cell_list(dataset, cell_date_list, cell_id,
                                 read_perc=1.0, max_runtime=None):
    """
    reads data from the dataset using the get_data method.
    In this method the start and end datetimes are fixed for all
    cell ID's that are read.

    Parameters
    ----------
    dataset: instance
        instance of a class that implements a get_data(date_start, date_end, cell_id)
        method
    date_start: datetime
        start dates which should be read.
    date_end: datetime
        end dates which should be read.
    cell_date_list: list of tuples, time intervals to read for each cell
    cell_id: int or iterable
        cell ids which should be read. can also be a list of integers
    read_perc : float
        percentage of cell ids to read from the
    max_runtime: int, optional
        maximum runtime of test in second.
    """
    # make sure cell_id is iterable
    try:
        iter(cell_id)
    except TypeError:
        cell_id = [cell_id]

    cell_read = random.sample(
        cell_id, int(math.ceil(len(cell_id) * read_perc / 100.0)))

    dates_read = random.sample(
        cell_date_list, int(math.ceil(len(cell_date_list) * read_perc / 100.0)))

    print "reading {} out of {} cells".format(len(cell_read), len(cell_id))
    start = time.time()
    for c, dates in zip(cell_read, dates_read):
        data = dataset.get_data(dates[0], dates[1], c)
        if max_runtime is not None:
            end = time.time()
            duration = end - start
            if duration > max_runtime:
                break
