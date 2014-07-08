'''
	Dataset Construction / Compilation Classes

	ALL Data Constructors Requires the separate Download of Source Data and the Specification of a Source Data Directory
	Note: Every effort will be made to keep the interface up to date if any dataset format or filenames change

	This Class will load the RAW Data from RAW Source Files from Various Formats, and undertake Standardization to Produce Harmonized Key Variables

	The main usefulness of Constructor Classes is to simply remove compilation code from the Core Objects

	Harmonisation:
	-------------
		1. 	country 	: 	iso3c 	(str)
		2. 	year 		: 	yyyy 	(int)
		3.  productcode : 	SITC or HS (str) 	Note: Str is used to prevent issues with leading 0's etc.

	Datasets:
	--------
		1. Feenstra/NBER Data 						[Last Checked: 03/07/2014]
		2. BACI Data
		3. CEPII Data
		4. UNCTAD Revealed Capital,Labour, and Land
		....

	Issues:
	-------
		1. 	How best to Incorporate the Source Dataset files. They can be very large 
			[Currently will pull in from a MyDatasets Object]
		2. 	This will be pretty slow to derive data each time from the raw data and will drive unnecessary wait times
			Current Direction: Separate Constructor Classes to Dataset Classes and pickle

	Future Work:
	-----------
		1. 	How to Handle Custom Altered Made Datasets such as Intertemporally Consistent NBER-BACI Data?
			Current Direction: Focus on making RAW Data Easily Acceptable such that alterations can be made by a Project without the initial setup
		2. 	Integrate simple md5sum Dataset Management from MyDatasets Project
'''

import pandas as pd
import numpy as np

# - Dataset Object - #
from .Dataset import NBERFeenstraWTF

# - Data Constructors - #

class GenericConstructor(object):
	'''
		Not Currently Required as will Integrate with ProductLevelExportSystem etc. (.from_csv())
	'''
	pass

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
	source_last_checked =  np.datetime64('2014-07-04')
	_fn_prefix			= u'wtf'
	_fn_postfix			= u'.dta'
	_raw_units 			= 1000
	
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
			years = self.available_years 	# Default Years
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
		dataset = NBERFeenstraWTF(data=self.raw_data, years=self.years, verbose=verbose)
		return dataset

	## - Clean Data Tasks - ##

	def standardize_data(self, verbose=False):
		'''
			Run Appropriate Standardization over the Raw Data
			
				[1] Countries to ISO3C Codes
				[2] SITC4 Values to Properly Formated STRINGS (Note: Dataset contains non-standard SITC rev 2 Codes)
				[3] Trade Values in $'s
		'''

		# - WORKING HERE - #

		raise NotImplementedError()





######## - IN WORK - ##########

class BACI(object):
	pass

class CEPII(object):
	pass

