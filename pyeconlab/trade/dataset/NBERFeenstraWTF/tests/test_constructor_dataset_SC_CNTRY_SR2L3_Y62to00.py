"""
Test Dataset: SC_CNTRY_SR2L3_Y62to00 from NBERFeenstraWTFConstructor
	
	dropAX 			: 	Drop AX Codes 
	sitcr2 			: 	Add SITCR2 Indicator
	drop_nonsitcr2 	: 	Drop non-standard SITC2 Codes
	report 			: 	Print Report
	source_institution : which institutions SITC classification to use

Datasets
--------
A => dropAX=False, sitcr2=False, drop_nonsitcr2=False
B => dropAX=True, sitcr2=True, drop_nonsitcr2=True

Stata Test Data
---------------
[1] Generated by ..\do\basic_sitc3_country_data.do

Future Work 
-----------
[1] Change TEST_DATA_DIR to a non hard linked reference. How do package this data?
[2] Consider using to_export, and to_import attributes rather than recomputing everything
"""

TEST_DATA_DIR 	= "E:\\work-data\\repos-pyeconlab-testdata\\" 
SOURCE_DATA_DIR = "E:\\work-data\\x_datasets\\36a376e5a01385782112519bddfac85e\\" #win7

import pandas as pd
from numpy.testing import assert_allclose

from pyeconlab import NBERFeenstraWTFConstructor

class TestSC_CNTRY_SR2L3_Y62to00():
	"""
	Test Suite for SC_CNTRY_SR2L3_Y62to00 Datasets A and B
	
	Settings
	--------
	A => dropAX=False, sitcr2=False, drop_nonsitcr2=False
	B => dropAX=True, sitcr2=True, drop_nonsitcr2=True
	C => dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True

	Stata Produced Files
	--------------------
	#-A-#
	A-nberfeenstra_do_stata_sitc3_country_data.log 					
	A-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta 	[OK]
	A-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta
	A-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta

	#-B-#
	B-nberfeenstra_do_stata_sitc3_country_data.log
	B-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta 	[OK]
	B-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta
	B-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta

	#-C-#
	C-nberfeenstra_do_stata_sitc3_country_data.log
	C-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta
	C-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta
	C-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta

	#-D-#
	D-nberfeenstra_do_stata_sitc3_country_data.log
	D-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta
	D-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta
	D-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta
	"""
	
	@classmethod
	def setUpClass(cls):
		cls.obj = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR)

	def setUp(self):
		self.obj.reset_dataset()

	#-Dataset A-#

	def test_bilateral_data_A(self):
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_A()
		#-stata-#
		self.A = pd.read_stata(TEST_DATA_DIR + 'A-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta')
		self.A = self.A.sort(['year', 'eiso3c', 'iiso3c', 'sitc3'])
		self.A = self.A.reset_index()
		del self.A['index']
		assert_allclose(self.obj.dataset['value'].values, self.A['value'].values)

	def test_export_data_A(self):
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_A(data='export') 											#a to_export would be more efficient here
		#-stata-#
		self.A = pd.read_stata(TEST_DATA_DIR + 'A-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta')
		self.A = self.A.sort(['year', 'eiso3c', 'sitc3'])
		self.A = self.A.reset_index()
		del self.A['index']
		assert_allclose(self.obj.dataset['value'].values, self.A['value'].values)

	def test_import_data_A(self): 																					#a to_import would be more efficient here
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_A(data='import')
		#-stata-#
		self.A = pd.read_stata(TEST_DATA_DIR + 'A-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta')
		self.A = self.A.sort(['year', 'iiso3c', 'sitc3'])
		self.A = self.A.reset_index()
		del self.A['index']
		assert_allclose(self.obj.dataset['value'].values, self.A['value'].values)

	#-Dataset B-#

	def test_bilateral_data_B(self):
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_B()
		#-stata-#
		self.B = pd.read_stata(TEST_DATA_DIR + 'B-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta')
		self.B = self.B.sort(['year', 'eiso3c', 'iiso3c', 'sitc3'])
		self.B = self.B.reset_index()
		del self.B['index']
		assert_allclose(self.obj.dataset['value'].values, self.B['value'].values)

	def test_export_data_B(self):
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_B(data='export') 											#a to_export would be more efficient here
		#-stata-#
		self.B = pd.read_stata(TEST_DATA_DIR + 'A-nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta')
		self.B = self.B.sort(['year', 'eiso3c', 'sitc3'])
		self.B = self.B.reset_index()
		del self.B['index']
		assert_allclose(self.obj.dataset['value'].values, self.B['value'].values)

	def test_import_data_B(self): 																					#a to_import would be more efficient here
		#-pyeconlab-#
		self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_B(data='import')
		#-stata-#
		self.B = pd.read_stata(TEST_DATA_DIR + 'A-nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta')
		self.B = self.B.sort(['year', 'iiso3c', 'sitc3'])
		self.B = self.B.reset_index()
		del self.B['index']
		assert_allclose(self.obj.dataset['value'].values, self.B['value'].values) 

	#-Dataset C-#

	# def test_bilateral_data_C(self):
	# 	#-pyeconlab-#
	# 	self.obj.construct_dataset_SC_CNTRY_SR2L3_Y62to00_C()
	# 	#-stata-#
	# 	self.C = pd.read_stata(TEST_DATA_DIR + 'C-nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta')
	# 	self.C = self.C.sort(['year', 'eiso3c', 'iiso3c', 'sitc3'])
	# 	self.C = self.C.reset_index()
	# 	del self.C['index']
	# 	assert_allclose(self.obj.dataset['value'].values, self.C['value'].values)
		
	#-Dataset D-#
