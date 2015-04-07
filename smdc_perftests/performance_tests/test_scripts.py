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
from smdc_perftests import helper


def run_performance_tests(name, dataset, save_dir,
                          gpi_list=None,
                          date_range_list=None,
                          gpi_read_perc=1.0,
                          date_read_perc=1.0,
                          repeats=5):
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
    gpi_read_perc: float, optional
        percentage of random selection from gpi_list read for each try
    date_read_perc: float, optioanl
        percentag of random selection from date_range_list read for each try
    repeats: int, optional
        number of repeats for each measurement
    """

    # test reading of time series by grid point/location id
    test_name = '{}_test-rand-gpi'.format(name)

    @test_cases.measure(test_name, runs=repeats)
    def test_rand_gpi():
        test_cases.read_rand_ts_by_gpi_list(dataset, gpi_list,
                                            read_perc=gpi_read_perc)

    results = test_rand_gpi()
    results.to_nc(os.path.join(save_dir, test_name + ".nc"))

    # test reading of daily images, only start date is given
    test_name = '{}_test-rand-daily-img'.format(name)

    # make date list containing just the start dates for reading images
    date_list = []
    for d1, d2 in date_range_list:
        date_list.append(d1)

    @test_cases.measure(test_name, runs=repeats)
    def test_rand_img():
        test_cases.read_rand_img_by_date_list(dataset, date_list,
                                              read_perc=date_read_perc)

    results = test_rand_img()
    results.to_nc(os.path.join(save_dir, test_name + ".nc"))

    # test reading of averaged images
    test_name = '{}_test-rand-avg-img'.format(name)

    @test_cases.measure(test_name, runs=repeats)
    def test_avg_img():
        test_cases.read_rand_img_by_date_range(dataset, date_range_list,
                                               read_perc=date_read_perc)

    results = test_avg_img()
    results.to_nc(os.path.join(save_dir, test_name + ".nc"))


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

        run_performance_tests(name, dataset, results_dir, gpi_list=dataset.grid.land_ind,
                              date_range_list=date_range_list, gpi_read_perc=0.1, repeats=1)

if __name__ == '__main__':
    path = os.path.join(
        "/media", "sf_D", "SMDC", "performance_tests", "CCI_testdata")
    run_esa_cci_netcdf_tests(
        os.path.join(path, "compr-4"), os.path.join(path, "results"))
