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
Tests basic functionality of the test_cases module
Created on Thu Nov 20 13:38:43 2014

@author: Christoph.Paulik@geo.tuwien.ac.at
'''

import smdc_perftests.performance_tests.test_cases as test_cases
import smdc_perftests.helper as helper
import datetime as dt
import time
import math
import pytest
from .fixtures import tempdir


class FakeDataset(object):

    """
    Fake Dataset that provides routines for reading
    time series and images
    that do nothing
    """

    def __init__(self, sleep_time=0.0001):
        pass
        self.ts_read = 0
        self.sleep_time = sleep_time
        self.img_read = 0
        self.cells_read = 0

    def get_timeseries(self, gpi, date_start=None, date_end=None):
        time.sleep(self.sleep_time)
        self.ts_read += 1
        return None

    def get_avg_image(self, date_start, date_end=None, cell_id=None):
        """
        Image readers generally return more than one
        variable. This should not matter for these tests.
        """
        time.sleep(self.sleep_time)
        assert type(date_start) == dt.datetime
        self.img_read += 1
        return None, None, None, None, None

    def get_data(self, date_start, date_end, cell_id):
        """
        Image readers generally return more than one
        variable. This should not matter for these tests.
        """
        time.sleep(self.sleep_time)
        assert type(date_start) == dt.datetime
        assert type(date_end) == dt.datetime
        self.cells_read += 1
        return None, None, None, None, None


def test_measure_output_format():
    """
    test if the measure decorator returns the
    results in the expected format
    """

    @test_cases.measure('test_output_format', runs=3)
    def test():
        time.sleep(0.5)

    results = test()
    assert results.n == 3
    assert len(results.confidence_int()) == 3


def test_run_rand_by_gpi_list():
    """
    tests run by gpi list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 10000 gpis of which 20 percent will be read
    gpi_list = range(10000)

    @test_cases.measure('test_rand_gpi', runs=3)
    def test():
        test_cases.read_rand_ts_by_gpi_list(fd, gpi_list)

    results = test()
    assert fd.ts_read == 10000 * 0.01 * 3


def test_run_rand_by_date_list():
    """
    tests run by date list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 1 year of dates of which 20 percent will be read
    date_list = []
    for days in range(365):
        date_list.append(dt.datetime(2007, 1, 1) + dt.timedelta(days=days))

    @test_cases.measure('test_rand_date', runs=3)
    def test():
        test_cases.read_rand_img_by_date_list(fd, date_list)

    results = test()
    assert fd.img_read == math.ceil(365 * 0.01) * 3


def test_run_rand_by_cell_list():
    """
    tests run by cell list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    cell_list = range(500)
    date_start = dt.datetime(2007, 1, 1)
    date_end = dt.datetime(2008, 1, 1)
    date_list = helper.generate_date_list(date_start, date_end, n=len(cell_list),
                                          max_spread=5, min_spread=5)

    @test_cases.measure('test_rand_cells', runs=3)
    def test():
        test_cases.read_rand_cells_by_cell_list(fd, date_list, cell_list)

    results = test()
    assert fd.cells_read == 500 * 0.01 * 3


def test_results_comparison():
    """
    Tests the comparison operators of
    the TestResults class
    """
    list1 = [5.8, 6.3, 6.2, 5.2, 4.3, 6.1, 4.2, 5.5]
    list2 = [6.7, 8.3, 9.4, 7.3, 8.5]
    list3 = [6.7, 8.3, 9.4, 7.3]

    res1 = test_cases.TestResults(list1, 'list1')
    res2 = test_cases.TestResults(list2, 'list2')
    res3 = test_cases.TestResults(list3, 'list3')

    assert res1 < res2
    assert res2 > res1
    assert not res1 < res3
    assert not res3 > res2


def test_TestResults_init():
    """
    tests if the correct exceptions are raised
    when a TestResults object is initialized
    wrongly
    """
    with pytest.raises(ValueError):
        res1 = test_cases.TestResults([1])


def test_to_netcdf(tempdir):
    """
    Writing to netCDF and reading again from file.
    """

    list1 = [5.8, 6.3, 6.2, 5.2, 4.3, 6.1, 4.2, 5.5]

    res1 = test_cases.TestResults(list1, 'list1')
    res1.to_nc("test.nc")

    res2 = test_cases.TestResults("test.nc")
    assert res1._measurements == res2._measurements
    assert res1.name == res2.name


def test_self_timing_dataset():
    fd = FakeDataset()
    std = test_cases.SelfTimingDataset(fd)

    std.get_timeseries(12)


def test_run_rand_by_gpi_list_self_timing():
    """
    tests run by gpi list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    std = test_cases.SelfTimingDataset(fd)
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 10000 gpis of which 20 percent will be read
    gpi_list = range(10000)

    @test_cases.measure('test_rand_gpi', runs=3)
    def test():
        test_cases.read_rand_ts_by_gpi_list(std, gpi_list)

    results = test()
    assert std.ts_read == 10000 * 0.01 * 3
    assert len(std.measurements['get_timeseries']) == 300


def test_run_rand_by_gpi_list_self_timing_max_runtime():
    """
    tests run by gpi list
    """
    fd = FakeDataset(sleep_time=0.01)
    std = test_cases.SelfTimingDataset(fd)
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 10000 gpis of which 20 percent will be read
    gpi_list = range(10000)

    @test_cases.measure('test_rand_gpi', runs=3)
    def test():
        test_cases.read_rand_ts_by_gpi_list(std, gpi_list, max_runtime=0.5)

    results = test()
    assert std.ts_read <= (10000 * 0.01 * 3) / 2
    assert len(std.measurements['get_timeseries']) <= 150


def test_run_rand_by_date_list_self_timing():
    """
    tests run by date list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    std = test_cases.SelfTimingDataset(fd)
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 1 year of dates of which 20 percent will be read
    date_list = []
    for days in range(365):
        date_list.append(dt.datetime(2007, 1, 1) + dt.timedelta(days=days))

    @test_cases.measure('test_rand_date', runs=3)
    def test():
        test_cases.read_rand_img_by_date_list(std, date_list)

    results = test()
    assert std.img_read == math.ceil(365 * 0.01) * 3
    assert len(std.measurements['get_avg_image']) == math.ceil(365 * 0.01) * 3


def test_run_rand_by_date_list_self_timing_max_runtime():
    """
    tests run by date list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset(sleep_time=0.1)
    std = test_cases.SelfTimingDataset(fd)
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 1 year of dates of which 4 images will be read
    date_list = []
    for days in range(365):
        date_list.append(dt.datetime(2007, 1, 1) + dt.timedelta(days=days))

    @test_cases.measure('test_rand_date', runs=3)
    def test():
        test_cases.read_rand_img_by_date_list(std, date_list, max_runtime=0.3)

    results = test()
    assert std.img_read == 9
    assert len(std.measurements['get_avg_image']) == 9


def test_run_rand_by_cell_list_self_timing():
    """
    tests run by cell list

    Does no assertions at the moment, but shows how to use
    the class
    """
    fd = FakeDataset()
    std = test_cases.SelfTimingDataset(fd)
    cell_list = range(500)
    date_start = dt.datetime(2007, 1, 1)
    date_end = dt.datetime(2008, 1, 1)
    date_list = helper.generate_date_list(date_start, date_end, n=len(cell_list),
                                          max_spread=5, min_spread=5)

    @test_cases.measure('test_rand_cells', runs=3)
    def test():
        test_cases.read_rand_cells_by_cell_list(std, date_list, cell_list)

    results = test()
    assert std.cells_read == 500 * 0.01 * 3
    assert len(std.measurements['get_data']) == std.cells_read


def test_run_rand_by_cell_list_self_timing_max_runtime():
    """
    tests run by cell list using a SelfTimingDataset and restricting the
    maximum runtime
    """
    fd = FakeDataset(sleep_time=0.1)
    std = test_cases.SelfTimingDataset(fd)
    cell_list = range(500)
    date_start = dt.datetime(2007, 1, 1)
    date_end = dt.datetime(2008, 1, 1)
    date_list = helper.generate_date_list(date_start, date_end, n=len(cell_list),
                                          max_spread=5, min_spread=5)

    @test_cases.measure('test_rand_cells', runs=3)
    def test():
        test_cases.read_rand_cells_by_cell_list(std, date_list, cell_list,
                                                max_runtime=0.4)

    results = test()
    assert std.cells_read == 12
    assert len(std.measurements['get_data']) == std.cells_read
if __name__ == '__main__':
    test_self_timing_dataset()
