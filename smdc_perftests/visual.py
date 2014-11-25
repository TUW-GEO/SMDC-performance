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
Module for visualizing the test results
Created on Tue Nov 25 13:44:56 2014

@author: Christoph.Paulik@geo.tuwien.ac.at
'''

try:
    import seaborn as sns
    seaborn_installed = True
except ImportError:
    seaborn_installed = False
    pass

import matplotlib.pyplot as plt


def plot_boxplots(*args, **kwargs):
    """
    plots means and confidence intervals
    of given TestResults objects

    Parameters
    ----------
    *args: TestResults instances
        any Number of TestResults instances that should be plotted
        side by side
    conf_level: int, optional
        confidence level to use for the computed confidence intervals

    **kwargs: varied
        all other keyword arguments will be passed on to the
        plt.subplots function

    Returns
    -------
    fig: matplotlib.Figure
    ax1: matplotlib.axes
    """
    if 'conf_level' in kwargs:
        conf_level = kwargs.pop('conf_level')
    else:
        conf_level = 95

    measurements = []
    conf_intervals = []
    means = []
    names = []
    for res in args:
        conf = res.confidence_int(conf_level=conf_level)
        measurements.append(res._measurements)
        conf_intervals.append([conf[0], conf[2]])
        means.append(res.mean)
        names.append(res.name)

    fig, ax1 = plt.subplots(**kwargs)
    if seaborn_installed:
        ax = sns.boxplot(measurements, conf_intervals=conf_intervals, notch=True,
                         usermedians=means)
    else:
        ax = plt.boxplot(measurements, conf_intervals=conf_intervals, notch=True,
                         usermedians=means)
    xtickNames = plt.setp(ax1, xticklabels=names)
    plt.setp(xtickNames)
    plt.title('Boxplots with notches at confidence level %d %%.' % conf_level)
    plt.ylabel('Time [s]')

    return fig, ax1
