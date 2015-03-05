
.. code:: python

    import smdc_perftests.performance_tests.test_runner as test_runner
    import time
    import datetime as dt
    import numpy as np
.. code:: python

    # define a fake Dataset class that implements the methods
    # get_timeseries, get_avg_image and get_data
    
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
            self.cells_read = 0
    
        def get_timeseries(self, gpi, date_start=None, date_end=None):
            time.sleep(0.01*np.random.rand(1))
            self.ts_read += 1
            return None
    
        def get_avg_image(self, date_start, date_end=None, cell_id=None):
            """
            Image readers generally return more than one
            variable. This should not matter for these tests.
            """
            assert type(date_start) == dt.datetime
            self.img_read += 1
            time.sleep(0.01*np.random.rand(1))
            return None, None, None, None, None
    
        def get_data(self, date_start, date_end, cell_id):
            """
            Image readers generally return more than one
            variable. This should not matter for these tests.
            """
            assert type(date_start) == dt.datetime
            assert type(date_end) == dt.datetime
            self.cells_read += 1
            time.sleep(0.01*np.random.rand(1))
            return None, None, None, None, None
    

.. code:: python

    fd = FakeDataset()
    # setup grid point index list, must come from grid object or
    # sciDB
    # this test dataset has 10000 gpis of which 1 percent will be read
    gpi_list = range(10000)
    
    @test_runner.measure('test_rand_gpi', runs=100)
    def test_ts():
        test_runner.read_rand_ts_by_gpi_list(fd, gpi_list)
    
    result_ts = test_ts()
    
    print result_ts
    


.. parsed-literal::

    
    Results test_rand_gpi
    100 runs
    median 0.5642 mean 0.5591 stdev 0.0334
    sum 55.9069
    95%% confidence interval of the mean
    upper 0.5657
           |
    mean  0.5591
           |
    lower 0.5524


.. code:: python

    # setup datetime list
    # this test dataset has 10000 days of dates of which 1 percent will be read
    date_list = []
    for days in range(10000):
        date_list.append(dt.datetime(2007, 1, 1) + dt.timedelta(days=days))
    
    @test_runner.measure('test_rand_date', runs=100)
    def test_img():
        test_runner.read_rand_img_by_date_list(fd, date_list)
    
    result_img = test_img()
    print result_img

.. parsed-literal::

    
    Results test_rand_date
    100 runs
    median 0.5530 mean 0.5548 stdev 0.0343
    sum 55.4800
    95%% confidence interval of the mean
    upper 0.5616
           |
    mean  0.5548
           |
    lower 0.5480


.. code:: python

    """
    Read data by cell list using fixed start and end date
    1 percent of the cells are read with a minimum of 1 cell.
    """
    fd = FakeDataset()
    cell_list = range(10000)
    
    @test_runner.measure('test_rand_cells', runs=100)
    def test():
        test_runner.read_rand_cells_by_cell_list(fd,
                                                 dt.datetime(2007, 1, 1), dt.datetime(2008, 1, 1), cell_list)
    
    results_cells = test()
    print results_cells


.. parsed-literal::

    
    Results test_rand_cells
    100 runs
    median 0.5510 mean 0.5476 stdev 0.0368
    sum 54.7624
    95%% confidence interval of the mean
    upper 0.5549
           |
    mean  0.5476
           |
    lower 0.5403


.. code:: python

    import smdc_perftests.visual as vis
    import matplotlib.pyplot as plt
    %matplotlib inline
    
    fig, axis = vis.plot_boxplots(result_ts, result_img, results_cells)
    plt.show()




.. image:: output_4_1.png

