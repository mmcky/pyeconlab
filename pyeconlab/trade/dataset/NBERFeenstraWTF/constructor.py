'''
	NBERFeenstraWTF Constructer

	Compile NBERFeenstra RAW data Files into an NBERFeenstraWTF Object

	Tasks:
	-----
		[1] Basic Cleaning of Data a) Add ISO3C country codes, b) Add SITCR2 Markers
'''

import os
import copy
import pandas as pd
import numpy as np

from dataset import NBERFeenstraWTF 
from pyeconlab.util import from_series_to_pyfile, check_directory 			#Reference requires installation!

# - Data in data/ - #
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "data")

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
	_exporters 			= None
	_importers 			= None 
	_country_list 		= None
	# - Dataset Attributes - #
	_name 				= u'NBERFeenstraWTF'
	source_web 			= u"http://cid.econ.ucdavis.edu/nberus.html"
	source_last_checked = np.datetime64('2014-07-04')
	complete_dataset 	= False 										#Make this harder to set
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
			self.complete_dataset = True	# This forces object to be imported based on the whole dataset
			years = self._available_years 	# Default Years
		# - Fetch Raw Data for Years - #
		source_dir = check_directory(source_dir) 	#Performs basic tests on the Specified Directory
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

	# - Properties - #

	@property
	def exporters(self):
		'''
			Returns List of Exporters
		'''
		if self._exporters == None:
			self._exporters = list(self.raw_data['exporter'].unique())
			self._exporters.sort()
		return self._exporters	

	def global_exporter_list(self):
		'''
			Return Global Sorted Unique List of Exporters
			Useful as Input to Concordances such as NBERFeenstraExporterToISO3C

			To Do:
			------
				[1] Should I write an Error Decorator? 
		'''
		if self.complete_dataset == True:
			return self.exporters
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	@property
	def importers(self):
		'''
			Returns List of Importers
		'''
		if self._importers == None:
			self._importers = list(self.raw_data['importer'].unique())
			self._importers.sort()
		return self._importers
	
	def global_importer_list(self):
		'''
			Return Global Sorted Unique List of Importers
			Useful as Input to Concordances such as NBERFeenstraImporterToISO3C
		'''
		if self.complete_dataset == True:
			return self.importers
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	@property
	def country_list(self):
		'''
			Returns a Country List (Union of Exporters and Importers)
		'''
		if self._country_list == None:
			self._country_list = list(set(self.exporters).union(set(self.importers)))
			self._country_list.sort()
		return self._country_list	

	# - Generate Files for data/ folder - #

	def generate_global_info(self, target_dir='data/', out_type='py', verbose=False):
		'''
			Construct Global Information About the Dataset 
			Automatically import ALL data and Construt:
				[1] Country List
				[2] Exporter List
				[3] Importer List

			Usage:
			-----
				Useful if NBER Feenstra's Dataset get's updated etc.

			Future Work:
			------------
				[1] Update so that the new files are saved in the package location, not a local folder
					Currently this will produce the files, that will need to be relocated to package
		'''

		if self.complete_dataset != True:
			raise ValueError("Dataset must be complete. Try running the constructor without defining years=[]")
		if out_type == 'csv':
			# - Exporters - #
			pd.Series(self.exporters).write_csv(target_dir + 'exporters_list.csv')
			# - Importers - #
			pd.Series(self.importers).write_csv(target_dir + 'importers_list.csv')
			# - Country List - #
			pd.Series(self.country_list).write_csv(target_dir + 'countryname_list.csv')
		elif out_type == 'py':
			# - Exporters - #
			s = pd.Series(self.exporters)
			s.name = 'exporters'
			from_series_to_pyfile(s, target_dir=target_dir, fl='exporters.py', docstring=self._name+': exporters'+'\n\t'+self.source_web)
			# - Importers - #
			s = pd.Series(self.importers)
			s.name = 'importers'
			from_series_to_pyfile(s, target_dir=target_dir, fl='importers.py', docstring=self._name+': importers'+'\n\t'+self.source_web)
			# - Country List - #
			s = pd.Series(self.country_list)
			s.name = 'countries'
			from_series_to_pyfile(s, target_dir=target_dir, fl='country_list.py', docstring=self._name+': country list'+'\n\t'+self.source_web)
		else:
			raise TypeError("out_type: Must be of type 'csv' or 'py'")


	## - Clean Data Tasks - ##

	def standardize_data(self,verbose=False):
		'''
			Run Appropriate Standardization over the Raw Data
			
				[1] Countries to ISO3C Codes
				[3] Trade Values in $'s

			Notes:
			-----
				[1] Raw Dataset has Non-Standard SITC rev2 Codes 
		'''
		from .data.exporters import exporters

		# - WORKING HERE - #


		# - Copy Data - #
		self.data = copy.deepcopy(self.raw_data) 
		# - Change Units to $'s - #
		self.data['value'] = self.data['value'] * 1000
		# - Update Country Names - #
		
