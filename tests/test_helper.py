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
Testing the helper module
Created on Wed Apr  1 15:21:15 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''


from datetime import datetime

from smdc_perftests import helper


def test_generate_date_list():
    """
    This is as method for testing this function
    but assertions are difficut if the datelist is
    generated randomly
    """
    minimum = datetime(2007, 01, 01)
    maximum = datetime(2012, 01, 01)
    # test for max_spread zero
    dl = helper.generate_date_list(minimum, maximum, n=10, max_spread=0)
    for d1, d2 in dl:
        assert d1 == d2
    dl = helper.generate_date_list(minimum, maximum, n=1000, max_spread=10)
    for d1, d2 in dl:
        assert (d2 - d1).days <= 10

if __name__ == '__main__':
    test_generate_date_list()
