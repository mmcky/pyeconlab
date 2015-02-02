"""
Test for Generic Dataset Function Against dissaggregated routines

Files
-----
constructor_dataset_sitcr2.py
constructor_dataset_sitcr2l3.py 
constructor_dataset_sitcr2l4.py

Notes
-----
1.  This suggests that the two dataframes are indeed equivalent and can consider 
    REMOVING the constructor_dataset_sitcr2l4 and constructor_dataset_sitcr2l3 items 
    in favour of the generic

"""

#-STATIC TEST DATA SOURCE-#
#-Note: For now I will use hard coded sources but this needs to be updated to be within the package-#

import sys
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal

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
from pyeconlab.util import package_folder

#-Package Data-#
TEST_DATA_DIR = package_folder(__file__, "data") 

#-DATASET Options-#
from ..constructor_dataset import SITC_DATASET_OPTIONS
DATA_TYPE = ['trade', 'export', 'import']

class TestGenericVsSpecificNBERFunctions():

    @classmethod
    def setUpClass(cls):
        cls.rawdata = load_raw_dataset(TEST_DATA_DIR+"nberwtf_raw_years-1990-1991-1992.h5", 1990, 1992, verbose=True)                       #Try 3 years
        cls.hkchina_rawdata = load_raw_dataset(TEST_DATA_DIR+"nberwtf_hkchina_supp_raw_years-1990-1991-1992.h5", 1990, 1992, verbose=True)

    def TestLevel4(self, verbose=True):
        """
        Test Level 4 Data Constructors
        """
        for dataset in SITC_DATASET_OPTIONS:
            if verbose: print "Testing DATASET Definition: %s" % dataset
            for data_type in DATA_TYPE:
                if verbose: print "Testing DATA_TYPE: %s" % data_type
                #-IF Adjust Hong Kong Data then Add Data to the Tuple-#
                if SITC_DATASET_OPTIONS[dataset]['adjust_hk'] == True: 
                    SITC_DATASET_OPTIONS[dataset]['adjust_hk'] = (True, self.hkchina_rawdata)
                else:
                    SITC_DATASET_OPTIONS[dataset]['adjust_hk'] = (False, None)
                data1 = construct_sitcr2(self.rawdata, data_type=data_type, level=4, **SITC_DATASET_OPTIONS[dataset])   #-Default Options-#
                data2 = construct_sitcr2l4(self.rawdata, data_type=data_type, **SITC_DATASET_OPTIONS[dataset])
                assert_frame_equal(data1, data2)

    def TestLevel3(self, verbose=True):
        """
        Test Level 3 Data Constructors
        """
        for dataset in SITC_DATASET_OPTIONS:
            if verbose: print "Testing DATASET Definition: %s" % dataset
            for data_type in DATA_TYPE:
                if verbose: print "Testing DATA_TYPE: %s" % data_type
                #-IF Adjust Hong Kong Data then Add Data to the Tuple-#
                if SITC_DATASET_OPTIONS[dataset]['adjust_hk'] == True: 
                    SITC_DATASET_OPTIONS[dataset]['adjust_hk'] = (True, self.hkchina_rawdata)
                else:
                    SITC_DATASET_OPTIONS[dataset]['adjust_hk'] = (False, None)
                data1 = construct_sitcr2(self.rawdata, data_type=data_type, level=3, **SITC_DATASET_OPTIONS[dataset])   #-Default Options-#
                data2 = construct_sitcr2l3(self.rawdata, data_type=data_type, **SITC_DATASET_OPTIONS[dataset])
                assert_frame_equal(data1, data2)