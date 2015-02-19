"""
Test for Generic Dataset Function Against dissaggregated routines

STATUS: IN-USE (2015-02-09)

Files
-----
constructor_dataset_sitcr2.py
constructor_dataset_sitcr2l3.py 
constructor_dataset_sitcr2l4.py

Notes
-----
1.  This suggests that the two dataframes are indeed equivalent and can consider 
    REMOVING the constructor_dataset_sitcr2l4 and constructor_dataset_sitcr2l3 items 
    in favour of the generic function

"""

#-STATIC TEST DATA SOURCE-#
#-Note: For now I will use hard coded sources but this needs to be updated to be within the package-#

import sys
import os
import re
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
from pyeconlab.trade.dataset.NBERWTF import construct_sitcr2l1, construct_sitcr2l2, construct_sitcr2l3, construct_sitcr2l4 
from pyeconlab.util import package_folder

#-Package Data-#
TEST_DATA_DIR = package_folder(__file__, "data") 

#-DATASET Options-#
from ..constructor_dataset import SITC_DATASET_OPTIONS
DATA_TYPE = ['trade', 'export', 'import']

class TestRandomSamples():
    """
    Test Random Samples in Each Dataset
    """

    @classmethod
    def setUpClass(cls):
        cls.raw_data = load_raw_dataset(TEST_DATA_DIR+"nberwtf_raw_years-1990-1991-1992.h5", 1990, 1990, verbose=True)
        cls.hkchina_rawdata = load_raw_dataset(TEST_DATA_DIR+"nberwtf_hkchina_supp_raw_years-1990-1991-1992.h5", 1990, 1990, verbose=True)

    def TestRandomRawSample1990(self):
        """
        Test Random Sample Data from 1990
        """
        pass

class TestOptions():
    """
    Test Options for the construct_sitcr2 function
    """
    @classmethod
    def setUpClass(cls):
        cls.rawdata = load_raw_dataset(TEST_DATA_DIR+"nberwtf_raw_years-1990-1991-1992.h5", 1990, 1990, verbose=True) 
        cls.hkchina_rawdata = load_raw_dataset(TEST_DATA_DIR+"nberwtf_hkchina_supp_raw_years-1990-1991-1992.h5", 1990, 1990, verbose=True)

    # def Test_dropax(self):
    #     """
    #     file: stata_wtf98_BGR_sitc4_51##_WORLD_import.csv                 ### ---> This is 1998 DATA -> Need 1990,1991 or 1992 DATA for within REPO testing <--- ###
    #     """
    #     OPTIONS = {
    #             'A' :   {   'dropAX' : False,                    
    #                         'sitcr2' : False,                     
    #                         'drop_nonsitcr2' : False,            
    #                         'adjust_hk' : (False, None),                 
    #                         'intertemp_cntrycode' : False,        
    #                         'drop_incp_cntrycode' : False,        
    #                         'adjust_units' : False,
    #                         'source_institution' : 'un',
    #                     },
    #             'B' :   {   'dropAX' : True,                     
    #                         'sitcr2' : False,                     
    #                         'drop_nonsitcr2' : False,             
    #                         'adjust_hk' : (False, None),                   
    #                         'intertemp_cntrycode' : False,        
    #                         'drop_incp_cntrycode' : False,        
    #                         'adjust_units' : False,
    #                         'source_institution' : 'un',
    #                     },
    #             }
    #     #-SITC Level 4-#
    #     #~~~~~~~~~~~~~~#
    #     #-Test dropAX=False Import Data-#
    #     A = construct_sitcr2(self.rawdata, data_type='import', level=4, **OPTIONS['A'])
    #     RAW = pd.read_csv(TEST_DATA_DIR + "stata_wtf98_BGR_sitc4_51##_WORLD_import.csv")
    #     for idx,row in RAW.iterrows():
    #         A_VAL = A.loc[(A.year == row.year) & (A.iiso3c == row.iiso3c) & (A.sitc4 == str(row.sitc4))]
    #         A_VAL = A_VAL.get_value(index=A_VAL.index[0], col='value')
    #         assert A_VAL == row.value
    #     #-Test DropAX=True Import Data-#
    #     B = construct_sitcr2(self.rawdata, data_type='import', level=4, **OPTIONS['B'])
    #     #-Prepare RAW DATA-#
    #     RAW = pd.read_csv(TEST_DATA_DIR + "stata_wtf98_BGR_sitc4_51##_WORLD_import.csv")
    #     RAW['AX'] = RAW.sitc4.apply(lambda x: 1 if re.search("[AX]", x) else 0)
    #     RAW = RAW.loc[RAW.AX != 1]
    #     del RAW['AX']
    #     #-Test Each Remaining Row of Data-#
    #     for idx,row in RAW.iterrows():
    #         B_VAL = B.loc[(B.year == row.year) & (B.iiso3c == row.iiso3c) & (B.sitc4 == str(row.sitc4))]
    #         B_VAL = B_VAL.get_value(index=B_VAL.index[0], col='value')
    #         assert B_VAL == row.value_adj

    def Test_sitcr2(self):
        raise NotImplementedError

    def Test_drop_nonsitcr2(self):
        raise NotImplementedError

    def Test_adjust_hk(self):
        """
        Test Difference between Hong Kong China Adjustment using a Random Sample
        random sample: stata_wtf90_hk_china_adjust_sitc4_check_sample.csv
        """
        OPTIONS = {
                'A' :   {   'dropAX' : False,                    
                            'sitcr2' : False,                     
                            'drop_nonsitcr2' : False,            
                            'adjust_hk' : (False, None),                 
                            'intertemp_cntrycode' : False,        
                            'drop_incp_cntrycode' : False,        
                            'adjust_units' : False,
                            'source_institution' : 'un',
                        },
                'B' :   {   'dropAX' : False,                     
                            'sitcr2' : False,                     
                            'drop_nonsitcr2' : False,             
                            'adjust_hk' : (True, self.hkchina_rawdata),                   
                            'intertemp_cntrycode' : False,        
                            'drop_incp_cntrycode' : False,        
                            'adjust_units' : False,
                            'source_institution' : 'un',
                        },
                }
        #-SITC Level 4-#
        A = construct_sitcr2(self.rawdata, data_type='trade', level=4, **OPTIONS['A'])
        B = construct_sitcr2(self.rawdata, data_type='trade', level=4, **OPTIONS['B'])
        RAW = pd.read_csv(TEST_DATA_DIR + "stata_wtf90_hk_china_adjust_sitc4_check_sample.csv")
        for idx,row in RAW.iterrows():
            A_VAL = A.loc[(A.year == row.year) & (A.iiso3c == row.iiso3c) & (A.eiso3c == row.eiso3c) & (A.sitc4 == str(row.sitc4))]
            if len(A_VAL) == 0:
                print "Data not contained in A"
                continue
            A_VAL = A_VAL.get_value(index=A_VAL.index[0], col='value')
            assert A_VAL == row.value
            B_VAL = B.loc[(B.year == row.year) & (B.iiso3c == row.iiso3c) & (B.eiso3c == row.eiso3c) & (B.sitc4 == str(row.sitc4))]
            if len(B_VAL) == 0:
                print "Data not contained in B"
                continue
            B_VAL = B_VAL.get_value(index=B_VAL.index[0], col='value')
            assert B_VAL == row.value_adj

class TestGenericVsSpecificNBERFunctions():
    """
    Test the Generic Function vs. Specific NBER Functions for Generating SITC Data for NBER WTF
    """

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

    def TestLevel2(self, verbose=True):
        """
        Test Level 2 Data Constructors
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
                data1 = construct_sitcr2(self.rawdata, data_type=data_type, level=2, **SITC_DATASET_OPTIONS[dataset])   #-Default Options-#
                data2 = construct_sitcr2l2(self.rawdata, data_type=data_type, **SITC_DATASET_OPTIONS[dataset])
                assert_frame_equal(data1, data2)

    def TestLevel1(self, verbose=True):
        """
        Test Level 1 Data Constructors
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
                data1 = construct_sitcr2(self.rawdata, data_type=data_type, level=1, **SITC_DATASET_OPTIONS[dataset])   #-Default Options-#
                data2 = construct_sitcr2l1(self.rawdata, data_type=data_type, **SITC_DATASET_OPTIONS[dataset])
                assert_frame_equal(data1, data2)