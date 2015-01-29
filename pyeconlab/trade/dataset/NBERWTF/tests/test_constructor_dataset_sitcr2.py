"""
Test for Generic Dataset Function Against dissaggregated routines

Files
-----
constructor_dataset_sitcr2.py
constructor_dataset_sitcr2l3.py 
constructor_dataset_sitcr2l4.py

Notes
-----
1. 	This suggests that the two dataframes are indeed equivalent and can consider 
	REMOVING the constructor_dataset_sitcr2l4 and constructor_dataset_sitcr2l3 items 
	in favour of the generic

"""

#-STATIC TEST DATA SOURCE-#
#-Note: For now I will use hard coded sources but this needs to be updated to be within the package-#

import sys
import os
import pandas as pd

if sys.platform.startswith('win'):
	DATA_DIR = r"D:/work-data/datasets/"
elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):             
    abs_path = os.path.expanduser("~")
    DATA_DIR = abs_path + "/work-data/datasets/"

SOURCE_DIR = DATA_DIR + "36a376e5a01385782112519bddfac85e" + "/"

#-END TEST SOURCE-#

#-Raw Data-#

def load_raw_dataset(fn, start_year, end_year, verbose=False):
    """
    Load Raw NBER Dataset
    """
    data = pd.DataFrame()
    for year in range(start_year, end_year+1, 1):
        print "Loading Year: %s" % year
        data = data.append(pd.read_hdf(fn, "Y%s"%year))
    if verbose: print data.year.unique()
    return data

from pyeconlab.trade.dataset.NBERWTF import construct_sitcr2
from pyeconlab.trade.dataset.NBERWTF import construct_sitcr2l3 
from pyeconlab.trade.dataset.NBERWTF import construct_sitcr2l4 

from pandas.util.testing import assert_frame_equal

class TestGenericVsSpecificNBERFunctions():

	@classmethod
	def setUpClass(cls):
		cls.rawdata = load_raw_dataset(SOURCE_DIR + 'nber_year.h5', 1970, 1971+1, verbose=True) 						#Try 2 years
		# cls.hk_rawdata = load_raw_dataset(SOURCE_DIR + 'nber_supp_year.h5', 1988, 2000+1, verbose=True)

	def TestLevel4(self):
		data1 = construct_sitcr2(self.rawdata, data_type='trade', level=4) 	#-Default Options-#
		data2 = construct_sitcr2l4(self.rawdata, data_type='trade')
		assert_frame_equal(data1, data2)

	def TestLevel3(self):
		data1 = construct_sitcr2(self.rawdata, data_type='trade', level=3) 	#-Default Options-#
		data2 = construct_sitcr2l3(self.rawdata, data_type='trade')
		assert_frame_equal(data1, data2)