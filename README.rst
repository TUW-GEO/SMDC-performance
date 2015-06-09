==============
SMDC_perftests
==============

This package **SMDC_perftests**, contains python modules that provide decorators
and classes for measuring execution time of function calls. On top of that
specific use cases needed during the Soil Moisture Data Cubes (SMDC) project are
implemented. Results are stored in a
:class:`SMDC_perftests.performance_tests.test_cases.TestResults` object. These
objects can be compared to each other to quickly find out if the measured time
was significantly different using a 95% confidence interval.

The objects can also be stored to and restored from netCDF4 files on disk.
There are also plotting functions for the TestResults object.

Sphinx Documentation
====================

Build the documentation with ``python setup.py docs``.


Unittest & Coverage
===================

Run ``python setup.py test`` to run all unittests defined in the subfolder
``tests`` with the help of `py.test <http://pytest.org/>`_. 
