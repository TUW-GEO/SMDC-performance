==============
SMDC_perftests
==============

This is the documentation of **SMDC_perftests**, a small python module that provides
a decorator for measuring the time a function needs to execute. It then stores the
results in a :class:`SMDC_perftests.performance_tests.test_runner.TestResults` object.
These objects can be compared to each other to quickly find out if the measured time
was significantly different using a 95% confidence interval.

The objects can also be stored to and restored from netCDF4 files on disk.
There are also plotting functions for the TestResults object.

Requirements
============

This package was tested using python2.7 and requires the packages

.. literalinclude:: ../requirements.txt


Contents
========

.. toctree::
   :maxdepth: 2

   Examples <examples>
   License <license>
   Module Reference <_rst/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
