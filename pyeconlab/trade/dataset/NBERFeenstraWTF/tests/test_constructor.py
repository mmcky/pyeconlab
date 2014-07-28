"""
Tests NBERFeenstra World Trade Flows (Constructor Object)

Test Suites:
-----------
[1] TestSmallSampleDataset 	: Test the Constructor for Logical Flaws (test attributes etc. on a small scale)
[2] TestConstructorAgainstKnownRawData : Test the Constructor with Real Raw Data 

Notes
-----
[1] Test Data is stored in ./data
[2] Use a Package Config file to determing locations of SOURCE_DIR etc. 
	Currently tuned to my DEV environment using "~/work-data"

Current Work:
------------
[1] TestConstructorAgainstKnownRawData - Needing Work
"""

import unittest
import copy
import pandas as pd
from pandas.util.testing import assert_series_equal

from pyeconlab.util import package_folder, expand_homepath, check_directory
from ..constructor import NBERFeenstraWTFConstructor

#-DATA Paths-#
SOURCE_DATA_DIR = check_directory("E:\\work-data\\x_datasets\\36a376e5a01385782112519bddfac85e\\") 			#Win7!
TEST_DATA_DIR = package_folder(__file__, "data") 

def import_csv_as_statatypes(fl):
	"""
	Import CSV Files so that dtype is the same as Stata Files 
	"""
	#-Import Types to Match Stata Import Types-#
	import_types = {
		    			'year' 		: int,
					    'icode'		: object,
					    'importer' 	: object,
					    'ecode'     : object,
					    'exporter'  : object,
					    'sitc4'     : object,
					    'unit'      : object,
					    'dot'       : float,
					    'value'     : int,
					    'quantity'  : float,
					}
	return pd.read_csv(fl, dtype=import_types)

class TestSmallSampleDataset(unittest.TestCase):
	""" 
	Tests NBERFeenstraWTFConstructor from a Small Sample Dataset

	Tests:
	-----
		[1] Attributes (Exporters, Importers)
		[2] Standardisation of Data
	"""

	def setUp(self):
		"""
		Import and Setup Class from a Small Known Dataset
		File: 'data/nberfeenstra_wtf62_random_sample.csv' (md5hash: da092cc4b8053083d53c5dc5b72df79d)
		Dependancies: import_csv_as_statatypes()
		"""
		#-Import Test Data-#
		self.df = import_csv_as_statatypes(TEST_DATA_DIR+"nberfeenstra_wtf62_random_sample.csv")
		self.obj = NBERFeenstraWTFConstructor(source_dir=TEST_DATA_DIR, skip_setup=True)
		self.obj.from_df(df=self.df)
		
		#-Known Solutions-#
		self.exp = set(['Canada', 'Cyprus', 'Jamaica', 'Poland', 'Spain', 'Taiwan', 'UK', 'World'])
		self.imp = set(['Cambodia','Canada','Czechoslovak', 'Ghana', 'Kenya', 'Korea Rep.','Mexico','Morocco', 'Switz.Liecht', 'USA'])

	def test_exporters(self):
		exp = self.exp
		obj = self.obj
		computed_exp = set(obj.exporters)
		assert exp == computed_exp, "Different Elements in the Set of Exporters: %s" % (exp.difference(computed_exp))
		
	def test_importers(self):
		imp = self.imp
		obj = self.obj
		computed_imp = set(obj.importers)
		assert imp == computed_imp, "Different Elements in the Set of Importers: %s" % (imp.difference(computed_imp))
		
	def test_standardisation(self):
		df = self.df
		obj = self.obj
		obj.set_dataset(df=copy.deepcopy(df[df.columns[0:10]])) 	#Remove Obs Columns
		obj.standardise_data()
		df2 = obj.dataset
		#-Importer Codes-#
		assert_series_equal(df2['iregion'], pd.Series(['13', '55', '21', '58', '16', '33', '45', '21', '45', '16'], name='iregion')) 				#Note: This is Order Specific!
		assert_series_equal(df2['iiso3n'], pd.Series(['504', '756', '840', '200', '288', '484', '116', '124', '410', '404'], name='iiso3n'))
		#-Exporter Codes-#
		assert_series_equal(df2['eregion'], pd.Series(['58', '44', '35', '10', '53', '21', '53', '53', '45', '53'], name='eregion'))
		assert_series_equal(df2['eiso3n'], pd.Series(['616', '196', '388', '000', '826', '124', '826', '724', '896', '826'], name='eiso3n'))


class TestConstructorAgainstKnownRawData(unittest.TestCase):
	"""
		Test the Constructor against random known data points.
		File:	'data/nberfeenstra_wtf62_random_sample.csv' (md5hash: da092cc4b8053083d53c5dc5b72df79d)
		Years: 	Conducting tests on 4-Year CrossSections [1962, 1985, 1990, 2000] 
	"""

	#-SetUp-#

	@classmethod
	def setUpClass(self):
		""" Setup NBERFeenstraWTFConstructor using: source_dir """
		years = [1962, 1985, 1990, 2000]
		self.obj = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, years=years, standardise_data=False, skip_setup=False, verbose=False)

	#-Basic Tests-#

	def test_years(self):
		""" Test setUpClass has imported the correct years"""
		obj = self.obj 
		yrs = obj['years'].unique()
		assert set(yrs) == set(self.years)

	def test_1962(self):
		""" 
		Tests for 1962 Data
		-----
		[1] number of observations
		[2] number of unique icountries and ecountries
		[3] number of unique sitc4 products
		"""
		pass

	def test_random_sample_1962(self):
		""" 
		Test a Random Sample from 1962
		File: 'data/nberfeenstra_wtf62_random_sample.csv' (md5hash: da092cc4b8053083d53c5dc5b72df79d)
		Dependancies: import_csv_as_statatypes()
		"""
		#-Load Random Sample From RAW DATASET-#
		years = [1962]
		rs = import_csv_as_statatypes(TEST_DATA_DIR+"nberfeenstra_wtf62_random_sample.csv") 		#random sample
		
	def test_1985(self):
		"""
		Tests for 1985 Data
		-----
		[1] number of observations
		[2] number of unique icountries and ecountries
		[3] number of unique sitc4 products		
		"""
		pass 
	
	def test_random_sample_1985(self):
		""" 
		Test a Random Sample from 1985
		File: 'data/nberfeenstra_wtf85_random_sample.csv' (md5hash: ???)
		Dependancies: import_csv_as_statatypes()
		"""
		#-Load Random Sample From RAW DATASET-#
		years = [1985]
		rs = import_csv_as_statatypes(TEST_DATA_DIR+"nberfeenstra_wtf85_random_sample.csv") 		#random sample
		pass

	def test_1990(self):
		"""
		Tests for 1990 Data
		-----
		[1] number of observations
		[2] number of unique icountries and ecountries
		[3] number of unique sitc4 products		
		"""
		pass 
	
	def test_random_sample_1990(self):
		""" 
		Test a Random Sample from 1990
		File: 'data/nberfeenstra_wtf90_random_sample.csv' (md5hash: ???)
		Dependancies: import_csv_as_statatypes()
		"""
		#-Load Random Sample From RAW DATASET-#
		years = [1990]
		rs = import_csv_as_statatypes(TEST_DATA_DIR+"nberfeenstra_wtf90_random_sample.csv") 		#random sample
		pass

	def test_2000(self):
		"""
		Tests for 2000 Data
		-----
		[1] number of observations
		[2] number of unique icountries and ecountries
		[3] number of unique sitc4 products		
		"""
		pass 
	
	def test_random_sample_2000(self):
		""" 
		Test a Random Sample from 2000
		File: 'data/nberfeenstra_wtf00_random_sample.csv' (md5hash: ???)
		Dependancies: import_csv_as_statatypes()
		"""
		#-Load Random Sample From RAW DATASET-#
		years = [2000]
		rs = import_csv_as_statatypes(TEST_DATA_DIR+"nberfeenstra_wtf00_random_sample.csv") 		#random sample
		pass


	def test_standardise_data(self):
		""" Test Standardisation of Data Method """
		#-Standardized Data-#
		self.obj.standardise_data()
		### --- WORKING HERE --- ###
		pass

	def test_china_hongkongdata(self):
		""" Test Import of China HongKong Adjustment Data """
		pass

	def test_adjust_china_hongkongdata(self):
		""" Test Adjustment of China & HongKong Data """
		pass
		self.obj.adjust_china_hongkongdata()

	def collapse_to_values_only(self):
		""" Test the Collapse to Export Values Only Against Some Random Test Cases """
		pass

	def test_bilateral_flows(self):
		""" Test Import of Bilateral Flows to Supp Data """
		pass

	### - Global Dataset Tests - ###

	def test_generate_global_info(self):
		""" Test Global Info Method """
		pass

	#-TearDown-#

	@classmethod
	def tearDownClass(self):
		""" Delete Large Memory Objects """
		pass


