# v0.5 - 2015-04-30

- added equi7 test runner
- fixed cell read percentage pass through to test runner
- added tests for the test runners
- set cells for each dataset in the test runner
- [0] for ESA CCI
- all cells over land for ASCAT
- [0, 1] for Equi 7
- installation now installes the netCDF files

# v0.4 - 2015-04-29

- added possibility to time each function call of the dataset functions
- added possibility to set maximum runtime of test execution

# v0.3 - 2015-04-07

- added classes for ESA CCI grid and netCDF reading
- added test_script which runs a whole suite of tests on a dataset
- added basic result loading and plotting

# v0.2 - 2015-03-05 #

- added reading using the get_data method and using a cell_list.
- changed the method signatures of a compatible dataset to those set in the
  meeting at AWST on 2015-02-24.
