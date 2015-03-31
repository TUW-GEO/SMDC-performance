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
Tests for the basic functionality of the ESA CCI dataset
Created on Tue Mar 31 10:18:44 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''

import os
import pytest
from datetime import datetime

import smdc_perftests.datasets.esa_cci as esa_cci


@pytest.yield_fixture()
def cci_ds():
    fname = os.path.join(
        os.path.dirname(__file__), "test_data", "ESACCI-2Images.nc")
    cci_reader = esa_cci.ESACCI(fname)
    yield cci_reader
    cci_reader.ds.close()


def test_locationid2rowcol(cci_ds):
    row, col = cci_ds.grid.gpi2rowcol(797106)
    assert row * 0.25 - 90 + 0.125 == 48.375
    assert col * 0.25 - 180 + 0.125 == 16.625


def test_get_timeseries(cci_ds):
    ts = cci_ds.get_timeseries(797106)
    pass


def test_land_points(cci_ds):
    assert cci_ds.land_ind.shape == (244243,)


def test_get_avg_image(cci_ds):
    img = cci_ds.get_avg_image(datetime(2013, 11, 30), datetime(2013, 12, 1))
    for v in img:
        assert img[v].shape == (720, 1440)
    pass


def test_get_data(cci_ds):
    img = cci_ds.get_data(datetime(2013, 11, 30), datetime(2013, 12, 1))
    for v in img:
        assert img[v].shape == (2, 720, 1440)
    pass
