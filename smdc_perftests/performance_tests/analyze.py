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
Module for analyzing and the test results
Created on Thu Apr  2 14:30:51 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''
import pandas as pd
import matplotlib.pyplot as plt

import smdc_perftests.performance_tests.test_cases as test_cases


def analyze_files(results_files, name_fm=None, grouping_f=None):
    """
    Takes a list of results file names and makes a few plots
    contrasting the measured times

    Parameters
    ----------
    results_files: list
        list of filenames to load
    name_fm: function, optional
        if set a function that gets the name of the results and
        returns a more meaningful name. This is useful if the names of
        the results are very long or verbose.
    grouping_f: function ,optional
        can be used to assign groups according to the name of the
        results. Gets the name and returns a string.
    """
    if name_fm is None:
        name_fm = lambda x: x
    if grouping_f is None:
        grouping_f = lambda x: 'means'

    d = {}
    names = []

    for fname in results_files:
        res = test_cases.TestResults(fname)
        name = name_fm(res.name)
        if name not in names:
            names.append(name)
        group = grouping_f(res.name)
        if group not in d:
            d[group] = []
        d[group].append(res.mean)

    df = pd.DataFrame(d, index=names)
    ax = df.plot(kind='bar')
    ax.set_yscale('log')
    plt.show()


def esa_cci_name_formatter(n):
    parts = n.split('_')
    chunking = parts[2]
    return chunking.split(',')[0]


def esa_cci_grouping(n):
    parts = n.split('_')
    rtype = parts[3]
    return '-'.join(rtype.split('-')[-2:])

if __name__ == '__main__':
    import glob
    import os

    path = os.path.join(
        "/media", "sf_D", "SMDC", "performance_tests", "CCI_testdata", "results")
    fs = glob.glob(os.path.join(path, "*.nc"))
    analyze_files(fs, name_fm=esa_cci_name_formatter,
                  grouping_f=esa_cci_grouping)
