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
Tests basic functionality of the test_runner module
Created on Thu Nov 20 13:38:43 2014

@author: Christoph.Paulik@geo.tuwien.ac.at
'''

import smdc_perftests.performance_tests.test_runner as test_runner
import datetime as dt
import time
import netCDF4
import pytest
from .fixtures import tempdir


class FakeDataset(object):

    """
    Fake Dataset that provides routines for reading
    time series and images
    that do nothing
    """

    def __init__(self):
        pass
        self.ts_read = 0
        self.img_read = 0

    def read_ts(self, gpi):
        time.sleep(0.0001)
        self.ts_read += 1
        return None

    def read_img(self, date):
        """
        Image readers generally return more than one
        variable. This should not matter for these tests.
        """
        assert type(date) == dt.datetime
        self.img_read += 1
        return None, None, None, None, None


def test_measure_output_format():
    """
    test if the measure decorator returns the
    results in the expected format
    """

    @test_runner.measure('test_output_format', runs=3)
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

    @test_runner.measure('test_rand_gpi', runs=3)
    def test():
        test_runner.read_rand_ts_by_gpi_list(fd, gpi_list)

    results = test()
    assert fd.ts_read == 10000 * 0.2 * 3


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

    @test_runner.measure('test_rand_date', runs=3)
    def test():
        test_runner.read_rand_img_by_date_list(fd, date_list)

    results = test()
    assert fd.img_read == 365 * 0.2 * 3


def test_results_comparison():
    """
    Tests the comparison operators of
    the TestResults class
    """
    list1 = [5.8, 6.3, 6.2, 5.2, 4.3, 6.1, 4.2, 5.5]
    list2 = [6.7, 8.3, 9.4, 7.3, 8.5]
    list3 = [6.7, 8.3, 9.4, 7.3]

    res1 = test_runner.TestResults(list1, 'list1')
    res2 = test_runner.TestResults(list2, 'list2')
    res3 = test_runner.TestResults(list3, 'list3')

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
        res1 = test_runner.TestResults([1])


def test_to_netcdf(tempdir):
    """
    Writing to netCDF and reading again from file.
    """

    list1 = [5.8, 6.3, 6.2, 5.2, 4.3, 6.1, 4.2, 5.5]

    res1 = test_runner.TestResults(list1, 'list1')
    res1.to_nc("test.nc")

    res2 = test_runner.TestResults("test.nc")
    assert res1._measurements == res2._measurements
    assert res1.name == res2.name
