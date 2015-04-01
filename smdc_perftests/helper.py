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
Helper functions
Created on Wed Apr  1 14:50:18 2015

@author: christoph.paulik@geo.tuwien.ac.at
'''

import random
from datetime import timedelta


def generate_date_list(minimum, maximum, n=500, max_spread=365):
    """
    Parameters
    ----------
    minimum: datetime
        minimum datetime
    maximum: datetime
        maximum datetime
    n: int
        number of dates to generate
    max_spread: int, optional
        maximum spread between dates

    Returns
    -------
    date_list: list
        list of start, end lists
        The format is a list of lists e.g.
        [[datetime(2007,1,1), datetime(2007,1,1)],
         [datetime(2007,1,1), datetime(2007,12,31)]]
    """
    date_list = []

    for i in range(n):
        delta_days = (maximum - minimum).days
        day_range = range(delta_days)
        day_start = random.choice(day_range)
        start_date = minimum + timedelta(days=day_start)
        end_date = start_date + timedelta(days=random.randint(0, max_spread))
        if end_date > maximum:
            end_date = maximum
        date_list.append([start_date, end_date])

    return date_list
