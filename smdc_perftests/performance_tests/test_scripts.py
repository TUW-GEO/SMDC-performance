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
Module implements the test cases specified in the performance test protocol
Created on Wed Apr  1 10:59:05 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''

import os
import glob
from datetime import datetime

from smdc_perftests.performance_tests import test_cases
from smdc_perftests.datasets import esa_cci
from smdc_perftests.datasets import ascat
from smdc_perftests import helper


def run_performance_tests(name, dataset, save_dir,
                          gpi_list=None,
                          date_range_list=None,
                          cell_list=None,
                          cell_date_list=None,
                          gpi_read_perc=1.0,
                          date_read_perc=1.0,
                          cell_read_perc=1.0,
                          max_runtime_per_test=None,
                          repeats=1):
    """
    Run a complete test suite on a dataset and store the results
    in the specified directory

    Parameters
    ----------
    name: string
        name of the test run, used for filenaming
    dataset: dataset instance
        instance implementing the get_timeseries,
        get_avg_image and get_data methods.
    save_dir: string
        directory to store the test results in
    gpi_list: list, optional
        list of possible grid point indices, if given the
        timeseries reading tests will be run
    date_range_list: list, optional
        list of possible dates, if given then the read_avg_image
        and read_data tests will be run.
        The format is a list of lists e.g.
        [[datetime(2007,1,1), datetime(2007,1,1)], #reads one day
         [datetime(2007,1,1), datetime(2007,12,31)]] # reads one year
    cell_list: list, optional
        list of possible cells to read from. if given then the read_data
        test will be run
    cell_date_list: list, optional
        list of time intervals to read per cell. Should be as long as the
        cell list or longer.
    gpi_read_perc: float, optional
        percentage of random selection from gpi_list read for each try
    date_read_perc: float, optioanl
        percentage of random selection from date_range_list read for each try
    cell_read_perc: float, optioanl
        percentage of random selection from cell_range_list read for each try
    max_runtime_per_test: float, optional
        maximum runtime per test in seconds, if given the tests will be aborted
        after taking more than this time
    repeats: int, optional
        number of repeats for each measurement
    """

    timed_dataset = test_cases.SelfTimingDataset(dataset)
    timed_avg_img_dataset = test_cases.SelfTimingDataset(dataset)

    if gpi_list is not None:
        # test reading of time series by grid point/location id
        test_name = '{}_test-rand-gpi'.format(name)

        @test_cases.measure(test_name, runs=repeats)
        def test_rand_gpi():
            test_cases.read_rand_ts_by_gpi_list(timed_dataset, gpi_list,
                                                read_perc=gpi_read_perc,
                                                max_runtime=max_runtime_per_test)

        results = test_rand_gpi()
        results.to_nc(os.path.join(save_dir, test_name + ".nc"))

        detailed_results = test_cases.TestResults(
            timed_dataset.measurements['get_timeseries'],
            name=test_name + "_detailed")

        detailed_results.to_nc(
            os.path.join(save_dir, test_name + "_detailed.nc"))

    if date_range_list is not None:
        # test reading of daily images, only start date is given
        test_name = '{}_test-rand-daily-img'.format(name)

        # make date list containing just the start dates for reading images
        date_list = []
        for d1, d2 in date_range_list:
            date_list.append(d1)

        @test_cases.measure(test_name, runs=repeats)
        def test_rand_img():
            test_cases.read_rand_img_by_date_list(timed_dataset, date_list,
                                                  read_perc=date_read_perc,
                                                  max_runtime=max_runtime_per_test)

        results = test_rand_img()
        results.to_nc(os.path.join(save_dir, test_name + ".nc"))

        detailed_results = test_cases.TestResults(
            timed_dataset.measurements['get_avg_image'],
            name=test_name + "_detailed")

        detailed_results.to_nc(
            os.path.join(save_dir, test_name + "_detailed.nc"))

        # test reading of averaged images
        test_name = '{}_test-rand-avg-img'.format(name)

        @test_cases.measure(test_name, runs=repeats)
        def test_avg_img():
            test_cases.read_rand_img_by_date_range(timed_avg_img_dataset, date_range_list,
                                                   read_perc=date_read_perc,
                                                   max_runtime=max_runtime_per_test)

        results = test_avg_img()
        results.to_nc(os.path.join(save_dir, test_name + ".nc"))

        detailed_results = test_cases.TestResults(
            timed_avg_img_dataset.measurements['get_avg_image'],
            name=test_name + "_detailed")

        detailed_results.to_nc(
            os.path.join(save_dir, test_name + "_detailed.nc"))

    if cell_list is not None and cell_date_list is not None:
        # test reading of complete cells
        test_name = '{}_test-rand-cells-data'.format(name)

        @test_cases.measure(test_name, runs=repeats)
        def test_read_cell_data():
            test_cases.read_rand_cells_by_cell_list(timed_dataset, cell_date_list, cell_list,
                                                    read_perc=cell_read_perc,
                                                    max_runtime=max_runtime_per_test)

        results = test_read_cell_data()
        results.to_nc(os.path.join(save_dir, test_name + ".nc"))

        detailed_results = test_cases.TestResults(
            timed_dataset.measurements['get_data'],
            name=test_name + "_detailed")

        detailed_results.to_nc(
            os.path.join(save_dir, test_name + "_detailed.nc"))


def run_esa_cci_netcdf_tests(test_dir, results_dir, variables=['sm']):
    """
    function for running the ESA CCI netCDF performance tests
    the tests will be run for all .nc files in the test_dir

    Parameters
    ----------
    test_dir: string
        path to the test files
    results_dir: string
        path in which the results should be stored
    variables: list
        list of variables to read for the tests
    """

    filelist = glob.glob(os.path.join(test_dir, "*.nc"))
    for filen in filelist:
        print "testing file", filen
        dataset = esa_cci.ESACCI_netcdf(filen, variables=variables)
        # get filename and use as name for test
        name = os.path.splitext(os.path.split(filen)[1])[0]
        # generate date list

        date_range_list = helper.generate_date_list(
            datetime(1980, 1, 1), datetime(2013, 12, 31), n=10000)

        run_performance_tests(name, dataset, results_dir,
                              gpi_list=dataset.grid.land_ind,
                              date_range_list=date_range_list,
                              gpi_read_perc=0.1, repeats=1)


def run_esa_cci_tests(dataset, testname, results_dir, n_dates=10000,
                      date_read_perc=0.1, gpi_read_perc=0.1,
                      repeats=3, cell_read_perc=10.0,
                      max_runtime_per_test=None):
    """
    Runs the ESA CCI tests given a dataset instance

    Parameters
    ----------
    dataset: Dataset instance
        Instance of a Dataset class
    testname: string
        Name of the test, used for storing the results
    results_dir: string
        path where to store the test restults
    n_dates: int, optional
        number of dates to generate
    date_read_perc: float, optioanl
        percentage of random selection from date_range_list read for each try
    gpi_read_perc: float, optional
        percentage of random selection from gpi_list read for each try
    repeats: int, optional
        number of repeats of the tests
    cell_list: list, optional
        list of possible cells to read from. if given then the read_data
        test will be run
    max_runtime_per_test: float, optional
        maximum runtime per test in seconds, if given the tests will be aborted
        after taking more than this time
    """

    date_start = datetime(1980, 1, 1)
    date_end = datetime(2013, 12, 31)

    date_range_list = helper.generate_date_list(date_start, date_end, n=n_dates)

    # test 500 "cells" with 500 months
    cell_list=[0]*500
    cell_date_list = helper.generate_date_list(date_start, date_end, n=len(cell_list))

    grid = esa_cci.ESACCI_grid()

    run_performance_tests(name=testname, dataset=dataset, save_dir=results_dir,
                          gpi_list=grid.land_ind,
                          date_range_list=date_range_list,
                          cell_list=cell_list,
                          cell_date_list=cell_date_list,
                          gpi_read_perc=gpi_read_perc,
                          date_read_perc=date_read_perc,
                          cell_read_perc=cell_read_perc,
                          max_runtime_per_test=max_runtime_per_test,
                          repeats=repeats)


def run_ascat_tests(dataset, testname, results_dir, n_dates=10000,
                    date_read_perc=0.1, gpi_read_perc=0.1, repeats=3,
                    cell_read_perc=10.0,
                    max_runtime_per_test=None):
    """
    Runs the ASCAT tests given a dataset instance

    Parameters
    ----------
    dataset: Dataset instance
        Instance of a Dataset class
    testname: string
        Name of the test, used for storing the results
    results_dir: string
        path where to store the test restults
    n_dates: int, optional
        number of dates to generate
    date_read_perc: float, optioanl
        percentage of random selection from date_range_list read for each try
    gpi_read_perc: float, optional
        percentage of random selection from gpi_list read for each try
    repeats: int, optional
        number of repeats of the tests
    cell_list: list, optional
        list of possible cells to read from. if given then the read_data
        test will be run
    max_runtime_per_test: float, optional
        maximum runtime per test in seconds, if given the tests will be aborted
        after taking more than this time
    """

    date_start = datetime(2007, 1, 1)
    date_end = datetime(2013, 12, 31)

    date_range_list = helper.generate_date_list(date_start, date_end, n=n_dates)
    grid = ascat.ASCAT_grid()

    cell_list=grid.get_cells()
    cell_date_list=helper.generate_date_list(date_start, date_end, n=len(cell_list))

    run_performance_tests(testname, dataset, results_dir,
                          gpi_list=grid.land_ind,
                          date_range_list=date_range_list,
                          date_read_perc=date_read_perc,
                          gpi_read_perc=gpi_read_perc,
                          cell_read_perc=cell_read_perc,
                          repeats=repeats,
                          cell_list=cell_list,
                          cell_date_list=cell_date_list,
                          max_runtime_per_test=max_runtime_per_test)


def run_equi7_tests(dataset, testname, results_dir, n_dates=10000,
                    date_read_perc=0.1, gpi_read_perc=0.1, repeats=3,
                    cell_read_perc=100.0,
                    max_runtime_per_test=None):
    """
    Runs the ASAR/Sentinel 1 Equi7 tests given a dataset instance

    Parameters
    ----------
    dataset: Dataset instance
        Instance of a Dataset class
    testname: string
        Name of the test, used for storing the results
    results_dir: string
        path where to store the test restults
    n_dates: int, optional
        number of dates to generate
    date_read_perc: float, optioanl
        percentage of random selection from date_range_list read for each try
    gpi_read_perc: float, optional
        percentage of random selection from gpi_list read for each try
    repeats: int, optional
        number of repeats of the tests
    cell_list: list, optional
        list of possible cells to read from. if given then the read_data
        test will be run
    max_runtime_per_test: float, optional
        maximum runtime per test in seconds, if given the tests will be aborted
        after taking more than this time
    """

    date_start = datetime(2015, 1, 8)
    date_end = datetime(2015, 2, 18)

    date_range_list = helper.generate_date_list(date_start, date_end, n=n_dates,
                                                max_spread=5, min_spread=5)

    gpi_list = range(2880000)
    cell_list = range(2) * 50

    cell_date_list=helper.generate_date_list(date_start, date_end, n=len(cell_list),
                                             max_spread=5, min_spread=5)

    run_performance_tests(testname, dataset, results_dir,
                          gpi_list=gpi_list,
                          date_range_list=date_range_list,
                          date_read_perc=date_read_perc,
                          gpi_read_perc=gpi_read_perc,
                          cell_read_perc=cell_read_perc,
                          repeats=repeats,
                          cell_list=cell_list,
                          cell_date_list=cell_date_list,
                          max_runtime_per_test=max_runtime_per_test)

if __name__ == '__main__':
    path = os.path.join(
        "/media", "sf_D", "SMDC", "performance_tests", "CCI_testdata")
    run_esa_cci_netcdf_tests(
        os.path.join(path, "compr-4"), os.path.join(path, "results"))
