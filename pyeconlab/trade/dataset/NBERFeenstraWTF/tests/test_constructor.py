"""
Tests NBERFeenstra World Trade Flows (Constructor Object)

Notes
-----
[1] Sample Data is stored in ./data
[2] Use a Package Config file to determing locations of SOURCE_DIR etc. Currently tuned to my DEV environment using "~/work-data"
"""

import unittest
from pyeconlab.util import package_folder, home_directory, check_directory

from ..constructor import NBERFeenstraWTFConstructor

#-DATA Paths-#
SOURCE_DATA_DIR = check_directory(home_directory() + "work-data")
TEST_DATA_DIR = package_folder(__file__, "data")

class TestNBERFeenstraWTFConstructor(unittest.TestCase):
	""" NBERFeenstraWTFConstructor Test Suite """

	def test_random_sample_1962(self):
		""" Test a Random Sample from 1962 """
		#-Load Random Sample From RAW DATASET-#
		years = [1962]
		wtf62rawsample = pd.read_csv(	TEST_DATA_DIR+"nberfeenstra_wtf62_random_sample.csv", 														\
										columns=['year','icode','importer','ecode','exporter','sitc4','unit','dot','value','quantity','obs']		\
									)
		exp = set(['Canada', 'Cyprus', 'Jamaica', 'Poland', 'Spain', 'Taiwan', 'UK', 'World'])
		imp = set(['Cambodia','Canada','Czechoslovak', 'Ghana', 'Kenya', 'Korea Rep.','Mexico','Morocco', 'Switz.Liecht', 'USA'])


		#-Test Attributes-#
		obj = NBERFeenstraWTFConstructor(source_dir=TEST_DATA_DIR, skip_setup=True)
		obj.from_csv(fl=TEST_DATA_DIR+"nberfeenstra_wtf62_random_sample.csv")
		#-Exporters-#
		computed_exp = set(obj.exporters)
		assert exp == computed_exp, "Different Elements in the Set of Exporters: %s" % (exp.difference(computed_exp))
		#-Importers-#
		compute_imp = set(obj.importers)
		assert imp == computed_imp, "Different Elements in the Set of Importers: %s" % (imp.difference(computed_imp))

		### --- WORKING HERE --- ###

		#-Construct Objects and Test-#
		#-Standardized Data-#
		a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, standardise=True, years=years)

		### --- WORKING HERE --- ###


	def test_adjust_china_hongkongdata(self):
		""" Test Adjustment of China & HongKong Data """
		pass

	def test_


	#- INWORK -#


	# def setUp(self):
	# 	"""
	# 	Construct Objects in Preparation for Testing
	# 	"""
	# 	self.a = NBERFeenstraWTFConstructor(source_dir='???', years=self.years)



