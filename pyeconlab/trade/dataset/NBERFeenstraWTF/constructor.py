'''
	NBERFeenstraWTF Constructer

	Compile NBERFeenstra RAW data Files into an NBERFeenstraWTF Object

	Tasks:
	-----
		[1] Basic Cleaning of Data a) Add ISO3C country codes, b) Add SITCR2 Markers
'''

import pandas as pd
import numpy as np

# - Dataset Object - #

from dataset import NBERFeenstraWTF 

class NBERFeenstraWTFConstructor(object):
	'''
		Data Constructor / Compilation Object for Feenstra NBER World Trade Data
		Years: 1962 to 2000
		Classification: SITC R2 L4
		Notes: Pre-1974 care is required for constructing intertemporally consistent data

		Interface:
		---------
		Source Directory: 	Specified by User
		Filename Format: 	wtf##.dta where ## is 62-00 	[03/07/2014]
							Note: Files currently need to be updated to the latest Stata .dta format MANUALLY

		Options:
		--------
			[1] 	standardize 	: 	This does not add or remove any data points. 
										It only adds standardized variables such as iso3c and productcode etc.  

		Future Work:
		-----------
			[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
	'''

	# - Attributes - #
	source_web 			= u"http://cid.econ.ucdavis.edu/nberus.html"
	source_last_checked = np.datetime64('2014-07-04')
	complete_dataset 	= False
	years 				= []
	_available_years 	= xrange(1962,2000+1,1)
	_fn_prefix			= u'wtf'
	_fn_postfix			= u'.dta'
	_raw_units 			= 1000
	_file_interface 	= [u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'unit', u'dot', u'value', u'quantity']
	# - Dataset Reference - #
	_mydataset_md5 		= u'36a376e5a01385782112519bddfac85e' 

	def set_fn_prefix(self, prefix):
		self._fn_prefix = prefix

	def set_fn_postfix(self, postfix):
		self._fn_postfix = postfix

	def __init__(self, source_dir, years=[], standardize=True, verbose=True):
		''' 
			Load RAW Data into Object
		'''
		if verbose: print "Fetching NBER-Feenstra Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True
			years = self._available_years 	# Default Years
		# - Fetch Raw Data for Years - #
		self.years 	= years
		self.raw_data 	= pd.DataFrame()
		for year in self.years:
			fn = source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Loading Year: %s from file: %s" % (year, fn)
			self.raw_data = self.raw_data.append(pd.read_stata(fn))
		# - Simple Standardization - #
		if standardize == True: 
			if verbose: print "Running Standardization updating 'exporter' -> 'exporteriso3c' etc."
			self.standardize_data(verbose=False)
		# - Generate Dataset Object - #
		#dataset = NBERFeenstraWTF(data=self.raw_data, years=self.years, verbose=verbose)
		#return dataset

	## - Clean Data Tasks - ##

	def standardize_data(self, verbose=False):
		'''
			Run Appropriate Standardization over the Raw Data
			
				[1] Countries to ISO3C Codes
				[3] Trade Values in $'s

			Notes:
			-----
				[1] Raw Dataset has Non-Standard SITC rev2 Codes 
		'''
		from ..concordance import NBERFeenstraExporterToISO3C
		# - Change Units to $'s - #
		self.raw_data['value'] = self.raw_data['value'] * 1000
		# - Update Country Names - #
		raise NotImplementedError()

	def generate_exporter_list(self):
		'''
			Return Unique List of Exporters
			Useful as Input to Concordances such as NBERFeenstraExporterToISO3C

			To Do:
			------
				[1] Should I write an Error Decorator? 
		'''
		if self.complete_dataset == True:
			exporters = self.raw_data['exporter'].unique()
			return list(exporters.sort())
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	def generate_importer_list(self):
		'''
			Return Unique List of Importers
			Useful as Input to Concordances such as NBERFeenstraImporterToISO3C
		'''
		if self.complete_dataset == True:
			importers = self.raw_data['importer'].unique()
			return list(importers.sort())
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	def reinit_info(self):
		'''
			Reconstruct Global Information About the Dataset 
			Automatically import ALL data and reconstruct:
				[1] Country List
				[2] Exporter List
				[3] Importer List

			Usage:
			-----
				Useful if NBER Feenstra's Dataset get's updated
		'''