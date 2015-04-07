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
Test of the performance scripts
Created on Tue Apr  7 14:32:23 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''


import os
import glob

from datetime import datetime
from smdc_perftests.performance_tests import test_scripts
from smdc_perftests.datasets.esa_cci import ESACCI_netcdf
from smdc_perftests import helper

from .fixtures import tempdir


def test_script_running(tempdir):
    fname = os.path.join(
        os.path.dirname(__file__), "test_data", "ESACCI-2Images.nc")
    # only read the sm variable for this testrun
    ds = ESACCI_netcdf(fname, variables=['sm'])
    # get the testname from the filename
    testname = os.path.splitext(os.path.split(fname)[1])[0]

    # generate a date range list using the helper function
    # in this example this does not make a lot of sense
    date_range_list = helper.generate_date_list(datetime(2013, 11, 30),
                                                datetime(2013, 12, 1),
                                                n=50)

    # set a directory into which to save the results
    # in this case the the tests folder in the home directory
    res_dir = os.path.join(".")
    # run the performance tests using the grid point indices from
    # the dataset grid, the generated date_range_list and gpi read percentage
    # of 0.1 percent and only one repeat
    test_scripts.run_performance_tests(testname, ds, res_dir,
                                       gpi_list=ds.grid.land_ind,
                                       date_range_list=date_range_list,
                                       gpi_read_perc=0.1,
                                       repeats=1)
    fs = glob.glob(os.path.join(res_dir, "*.nc"))
    assert len(fs) == 3
    flist = ["./ESACCI-2Images_test-rand-avg-img.nc",
             "./ESACCI-2Images_test-rand-gpi.nc",
             "./ESACCI-2Images_test-rand-daily-img.nc"]
    assert sorted(fs) == sorted(flist)
