# -*- coding: utf-8 -*-
"""
NBERWTF Constructor

Compile NBERFeenstra RAW data Files and Perform Data Preparation Tasks

It is the CORE responsibility of this module to clean, prepare and investigate the data.
The NATURE of the data shouldn't be changed in this class. For example, routines for collapsing the bilateral flows to exports should be contained in NBERWTF 

Conventions
-----------
__raw_data 	: Should be an exact copy of the imported files and protected. 
dataset 	: Contains the Modified Dataset

Notes
-----
A) Load Times
	[1] a = NBERWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='hdf') [~41s] 		From a complevel=9 file (Filesize: 148Mb)
	[2] a = NBERWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='hdf') [~34.5s]   	From a complevel=0 file (FileSize: 2.9Gb)
	[3] a = NBERWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='dta') [~14min 23s]

B) Convert Times (from a = NBERWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='dta'))
	[1] a.convert_raw_data_to_hdf(complevel=0) [1min 21seconds]
	[2] a.convert_raw_data_to_hdf(complevel=9) [2min 54seconds]

Outcome: Default complevel=9 (Doubles the conversion time but load time isn't significantly deteriorated)

Future Work
-----------
[1] A More memory efficient for Export and Import Data Only would be to collapse prior to adjustments?
[2] Clarify operators on raw_data vs. dataset
"""

from __future__ import division

import os
import copy
import re
import gc
import pandas as pd
import numpy as np
import countrycode as cc

from .dataset import NBERWTFTrade, NBERWTFExport, NBERWTFImport 
from pyeconlab.util import 	from_series_to_pyfile, check_directory, recode_index, merge_columns, check_operations, update_operations, from_idxseries_to_pydict, \
							countryname_concordance, concord_data, random_sample, find_row, assert_merged_series_items_equal
from pyeconlab.trade.classification import SITC

# - Data in data/ - #
this_dir, this_filename = os.path.split(__file__)
#DATA_PATH = check_directory(os.path.join(this_dir, "data"))
META_PATH = check_directory(os.path.join(this_dir, "meta"))

#-Concordances-#
from pyeconlab.country import iso3n_to_iso3c, iso3n_to_name 			#Why does this import prevent nosetests from running?				

class NBERWTFConstructor(object):
	"""
	Data Constructor / Compilation Object for Feenstra NBER World Trade Data
	Years: 	1962 to 2000
	Classification: SITC R2 L4 (Not Entirely Standard)
	Notes: 	Pre-1974 and Pre-1984 care is required for constructing intertemporally or dynamically consistent data
			(Check .dynamic_dataset())

	Interface:
	---------
	Source Directory: 	Specified by source_dir
	Filename Format: 	wtf##.dta where ## is 62-00 	[03/07/2014]
						Note: Files currently need to be updated to the latest Stata .dta format MANUALLY

	Variables
	---------
	DOT 		:	Direction of trade (1=Data from importer, 2=Data from exporter) [DOT=1 => CIF; DOT=2 => FOB]
	SITC 		: 	Standard International Trade Classification Revision 2
	ICode 		: 	Importer country code
	ECode 		: 	Exporter country code
	Importer 	: 	Importer country name
	Exporter 	: 	Exporter country name
	Unit 		: 	Units or measurement (see below)
	Year 		: 	4-digit year
	Quantity 	: 	Quantity (only for years 1984 – 2000)
	Value 		: 	Nominal Thousands of US dollars


	Summary of Important Documentation:
	-----------------------------------
	Values:
	------
		years 	: 	1962-2000
		units 	: 	Thousands of US dollars

	Quantity:
	---------
		years 	: 	1984-2000
		units 	: 	A Area (1,000 square meters) 
					H Energy (1,000 kilowatt hours)
					K Weight (kilograms)
					L Length (1,000 meters)
					N Units (number of items)
					P Pairs (number of pairs)
					V Volume (cubic meters)
					W Weight (metric tons)

	ProductCodes:
	-------------

		SITC Rev 1
		----------
			years 	: 	1962-1983 [Converted to SITC R2 [Section 2 of Documentation PDF]]
								  [Table #3: SITC Rev1 and SITC Rev2 Concordance]
						Note: This produces some dynamic inconsistencies if working over time. 

		SITC Rev 2
		----------
			years 	: 	1984-2000

		Notes:
		------
		[1] A and X codes for 1984-2000 (Not all Countries)

		[2] Codes Ending in 0: "4-digit SITC codes ending in zero were introduced into the data because we substituted the U.S.
				values of exports and imports in place of the UN values, whenever the U.S. was a partner. In the
				U.S. values, an SITC Rev. 2 code ending in zero has the same meaning as a code ending in A or
				X; that is, it represents trade within that 3-digit code that could not be accurately assigned to a 4-
				digit code. For example, trade within SITC 0220 really means trade within one of the SITC
				industries 0222, 0223, or 0224." [FAQ]

		[3] I am not currently sure what these SITC codes are. 
			I have requested further information from Robert Feenstra
			They only occur in 1962 - 1965 and have a combined value of: $6,683,000
			0021 	[Associated only with Malta]
			0023 	[Various Eastern European Countries and Austria]
			0024
			0025
			0031
			0035
			0039
			2829	[Assume: 282 NES. The MIT MediaLabs has this as “Waste and scrap metal of iron or steel” ]
			Note: Currently these items will be dropped. See delete_productcode_issues_with_raw_data():

		[4] There are currently 28 observations with no SITC4 codes. See issues_with_raw_data(),  See delete_issues_with_raw_data()

	CountryCodes
	------------
		[1] icode & ecode are structured: XXYYYZ => UN-REGION [2] + ISO3N [3] + Modifier [1]
		[2] Default Dataset should Match on ISO3N and merge in ISO3C from pyeconlab.country.concordance (iso3n_to_iso3c)

	Types of Operations
	-------------------
		[1] Reduction/Collapse 	: 	This collapses data and applies a function like ADD to lines with the same idx 
									These need to happen BEFORE adjust methods
		[2] Merge 				: 	Merge methods that add data (such as Hong Kong adjusted data etc.)
		[3] Adjust 				: 	Adjust Methods alter the data but don't change it's length (spliting codes etc.)

		Order of Operations: 	Reduction/Collapse -> Merge -> Adjust

	Organisation of Class:
	----------------------
		[1] Attributes
		[2] Internal Methods (__init__())
		[3] Properties
		[4] Supplementary Data (Loading Data)
		[5] Operations on Dataset (Adjusting self._dataset, cleaning tasks etc)
		[6] Construct Datasets (NBERWTF)
		[7] Supporting Functions
		[8] Generate Meta Data Files For Inclusion into Project Package (meta/)
		[9] Converters (hd5 Files etc.)
		[10] Generate Data to support construction of tests
		[11] Construct Case Study Data

	Notes:
	------
		[1] There should only be ONE assignment in __init__ to the __raw_data attribute [Is there a way to enforce this?]
			Any modification prior to returning an NBERWTF object should be carried out on "._dataset"
		[2] All Methods in this Class should operate on **NON** Indexed Data
		[3] This Dataset Requires ~25GB of RAM

	Future Work:
	-----------
		[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
		[2] When constructing meta/ data for inclusion in the package, it might be better to import from .dta files directly the required information
			For example. CountryCodes only needs to bring in a global panel of countrynames and then that can be converted to countrycodes
			[Update: This is currently not possible due to *.dta files being binary]
		[3] Move op_string work and turn it into a decorator function
		[5] Construct a BASE Constructor Class that contains generic methods (like IO)
	  **[6] Construct more formalised structure to ensure raw_data isn't operated on except split_countrycodes (OR should this always work on dataset?)
	"""

	# - Attributes - #

	_exporters 			= None 						#These are defined due to property check to None. But these could be removed if property just try/except
	_importers 			= None 
	_country_list 		= None
	_dataset 			= None 									

	# - Dataset Attributes - #

	_name 				= u'NBERWTF'
	classification 		= u'SITC'
	revision 			= 2
	source_web 			= u"http://cid.econ.ucdavis.edu/nberus.html"
	source_last_checked = np.datetime64('2014-07-04')
	complete_dataset 	= False 										#Make this harder to set with self.__?
	years 				= []
	level 				= 4
	operations 			= ''
	_available_years 	= xrange(1962,2000+1,1)
	_fn_prefix			= u'wtf'
	_fn_postfix			= u'.dta'
	_source_dir 		= None
	_raw_units 			= 1000
	_file_interface 	= [u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'unit', u'dot', u'value', u'quantity']
	notes 				= ""

	# - Other Data in NBER Feenstra WTF -#
	_supp_data 			= dict
	
	# - Dataset Reference - #
	__raw_data_hdf_fn 	= u'wtf62-00_raw.h5'
	__raw_data_hdf_yearindex_fn = u'wtf62-00_yearindex.h5'

	def __init__(self, source_dir, years=[], ftype='hdf', standardise=False, skip_setup=False, force=False, reduce_memory=False, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 		: 	Must contain the raw stata files (*.dta)
		years 			: 	Apply a Year Filter [Default: ALL]
		ftype 			: 	File Type ['dta', 'hdf'] [Default 'hdf' -> however it will generate on if not found from 'dta']
		standardise 	: 	Include Standardised Codes (Countries: ISO3C etc.)
		skip_setup 		: 	[Testing] This allows you to skip __init__ setup of object to manually load the object with csv data etc. 
							This is mainly used for loading test data to check attributes and methods etc. 
		force 			: 	If not working with the full dataset you may enter force=True to run standardisation routines etc.
							[Warning: This will not return Intertemporally Consistent Concordances]
		reduce_memory	: 	This will delete self.__raw_data after initializing self._dataset with the raw_data
							[Warning: This will render properties that depend on self.__raw_data inoperable]
							Usage: Useful when building datasets to be more memory efficient as the operations don't require a record of the original raw_data
							[Default: False] Only Saves ~2GB of RAM
		
		"""
		#-Assign Source Directory-#
		self._source_dir 	= check_directory(source_dir) 	# check_directory() performs basic tests on the specified directory

		#-Parse Skip Setup-#
		if skip_setup == True:
			print "[INFO] Skipping Setup of NBERWTFConstructor!"
			self.__raw_data 	= None 												#Allows to be assigned later on
			return None
		
		#-Setup Object-#
		if verbose: print "Fetching NBER-Feenstra Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True	# This forces object to be imported based on the whole dataset
			years = self._available_years 	# Default Years
		#-Assign to Attribute-#
		self.years 	= years

		# - Fetch Raw Data for Years - #
		if ftype == 'dta':
			self.load_raw_from_dta(verbose=verbose)
		elif ftype == 'hdf':
			try:
				self.load_raw_from_hdf(years=years, verbose=verbose)
			except:
				print "[INFO] Your source_directory: %s does not contain h5 version.\n Starting to compile one now ...."
				self.load_raw_from_dta(verbose=verbose)
				self.convert_raw_data_to_hdf(verbose=verbose) 			#Compute hdf file for next load
				self.convert_stata_to_hdf_yearindex(verbose=verbose)	#Compute Year Index Version Also
		else:
			raise ValueError("ftype must be dta or hdf")

		#-Reduce Memory-#
		if reduce_memory:
			self._dataset = self.__raw_data 									#Saves ~2Gb of RAM (but cannot access raw_data)
			self.__raw_data = None
		else:
			self._dataset = self.__raw_data.copy(deep=True) 					#[Default] pandas.DataFrame.copy(deep=True) is much more efficient than copy.deepcopy()

		#-Simple Standardization-#
		if standardise == True: 
			if verbose: print "[INFO] Running Interface Standardisation ..."
			self.standardise_data(force=force, verbose=verbose)


	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years)								+ \
				 "Complete Dataset: %s\n" % (self.complete_dataset) 		+ \
				 "Source Last Checked: %s\n" % (self.source_last_checked)
		#-Parse TestData Indicator-#
		try:
			if self.test_data == True:
				string += "\n[WARNING] TEST DATA LOADED IN OBJECT\n"
		except:
			pass
		return string
		
	# - Object Properties - #

	def set_fn_prefix(self, prefix):
		self._fn_prefix = prefix

	def set_fn_postfix(self, postfix):
		self._fn_postfix = postfix

	# - Raw Data Properties - #

	@property
	def raw_data(self):
		""" Raw Data Property to Return Private Attribute """ 
		try:
			return self.__raw_data.copy(deep=True)  							#Always Return a Copy
		except: 																#Load from h5 file
			self.load_raw_from_hdf(years=self.years, verbose=False)
			return self.__raw_data

	def del_raw_data(self, force):
		""" Delete Raw Data """
		if force == True:
			self.__raw_data = None

	@property
	def raw_data_operations(self):
		"""
		Check RAW data operations. 
		Note: This should be 'None' now that ALL operations have moved to dataset
		"""	 
		try: 
			return self.__raw_data.operations
		except: 
			return None 	#No Operations Applied

	def set_raw_data(self, df, force=False):
		"""
		Force Set raw_data (used for testing)
		"""
		if type(self.__raw_data) == pd.DataFrame:
			if force == False:
				print "[WARNING] To force the replacement of raw_data use 'force'=True"
				return None
		self.__raw_data =  df 	#Should this make a copy?

	@property
	def exporters(self):
		""" Returns List of Exporters (from Raw Data) """
		if self._exporters == None:
			self._exporters = list(self.__raw_data['exporter'].unique())
			self._exporters.sort()
		return self._exporters	

	def global_exporter_list(self):
		"""
		Return Global Sorted Unique List of Exporters
		Useful as Input to Concordances such as NBERFeenstraExporterToISO3C

		Future Work:
		------------
			[1] Should I write an Error Decorator? 
		"""
		if self.complete_dataset == True:
			return self.exporters
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	@property
	def importers(self):
		""" Returns List of Importers (from Raw Data) """
		if self._importers == None:
			self._importers = list(self.__raw_data['importer'].unique())
			self._importers.sort()
		return self._importers
	
	def global_importer_list(self):
		"""
		Return Global Sorted Unique List of Importers
		Useful as Input to Concordances such as NBERFeenstraImporterToISO3C
		"""
		if self.complete_dataset == True:
			return self.importers
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	@property
	def country_list(self):
		""" Returns a Country List (Union of Exporters and Importers) """
		if self._country_list == None:
			self._country_list = list(set(self.exporters).union(set(self.importers)))
			self._country_list.sort()
		return self._country_list	

	@property
	def supp_data(self, item):
		""" Return an Item from the Supplementary Data Dictionary """
		return self._supp_data[item]

	@property 
	def supp_data_items(self):
		""" Return a List of Items Available in Supplementary Data """
		items = []
		for key in self._supp_data.keys():
			if type(self._supp_data[key]) == pd.DataFrame:
				items.append(key)
		return sorted(items)

	@property 
	def dataset(self):
		""" Dataset contains the Exportable Result to NBERWTF """
		try:
			return self._dataset 
		except: 											#-Raw Data Not Yet Copied-#
			self._dataset = self.__raw_data.copy(deep=True)
			return self._dataset

	def reset_dataset(self, verbose=True):
		""" Reset Dataset to raw_data """
		if type(self.__raw_data) != pd.DataFrame:
			raise ValueError("RAW DATA is not a DataFrame! Most likely it has been deleted")
		if verbose: print "[INFO] Reseting Dataset to Raw Data"
		del self._dataset 																			#Clean-up old dataset
		self._dataset = self.__raw_data.copy(deep=True)
		self.operations = ''
		self.level = 4

	def set_dataset(self, df, force=False, reset_operations=True):
		""" 
		Check if Dataset Exists Prior to Assignment
		Q: Is this ever going to be used?
		"""
		if type(self._dataset) == pd.DataFrame:
			if force == False:
				print "[WARNING] The dataset attribute has previously been set. To force the replacement use 'force'=True"
				return None
		self._dataset =  df 							#Should this make a copy?
		if reset_operations:
			print "[INFO] Reseting operations attribute"
			self.operations = ''

	@property
	def verify_raw_data(self):
		if len(self.raw_data) != 27573764:
			return False
		if self.raw_data['value'].sum() != 337094011179.25201:
			return False 
		if self.raw_data['quantity'].sum() != 10302685608925.896:
			return False
		return True


	def stats(self, dataset=True, basic=False, extended=False, dlimit=10):
		""" Print Some Basic Statistics about the Dataset or RAW DATA """
		if dataset:
			df = self.dataset
			msg = "Dataset (%s) Statistics\n-------------------------------\n" % self._name
		else:
			df = self.raw_data
			msg = "Raw Data (%s) Statistics\n-------------------------------\n" % self._name
		msg += "Years: %s\n" % self.years
		msg += "Observations: %s; Variables: %s\n" % (df.shape[0], df.shape[1])
		if basic:
			print msg
			return None
		for col in df.columns:
			if col in ['value', 'quantity']:
				continue
			uniq = list(df[col].unique())
			msg += "Column: '%s' has %s Unique Entries\n" % (col, len(uniq))
			if extended:
					if len(uniq) >= dlimit:
						msg += "Items => %s ... %s\n" % (uniq[:int(dlimit/2)], uniq[-int(dlimit/2):])
					else:
						msg += "Items => %s\n" % uniq
		print msg 

	def exporter_total_values(self, data, key='exporter', year=False):
		""" 
		Return Exporter Total Values DataFrame by Year

		dataset : 	property (a.raw_data or a.dataset)
		key 	: 	'exporter' or 'ecode'
		year 	: 	Include 'year' [True/False]

		"""
		if year:
			return data.groupby(['year', key]).sum()['value']
		return data.groupby([key]).sum()['value']

	def importer_total_values(self, data, key='importer', year=False):
		""" 
		Return Exporter Total Values DataFrame

		dataset : 	property (a.raw_data or a.dataset)
		key 	: 	'importer' or 'icode'
		year 	: 	Include 'year' [True/False]

		"""
		if year:
			return data.groupby(by=['year', key]).sum()['value']
		return data.groupby(by=[key]).sum()['value']

	def to_exports(self, dataset=False, verbose=True):
		""" 
		Collapse Data to Exporters
		Note: Care must be taken with idx construction
		"""
		if verbose: print "[INFO] Collapsing to Exports"
		if dataset:
			data = self.dataset.copy(deep=True)
		else:
			data = self.raw_data.copy(deep=True)
		subidx = set(data.columns)
		for ritem in ['importer', 'icode', 'quantity', 'unit', 'iiso3c', 'iiso3n', 'iregion', 'imod', 'dot']: 			#Add and Removal Lists to Dataset Object?
			try:
				subidx.remove(ritem)
			except:
				pass
		gidx = subidx.copy()
		gidx.remove('value')
		data = data[list(subidx)].groupby(list(gidx)).sum() 		#Aggregate 'value'
		return data

	# ------ #
	# - IO - #
	# ------ #

	def load_raw_from_dta(self, verbose=True):
		"""
		Load RAW *.dta files from a source_directory
		
		Notes
		-----
		[1] Move to Generic Class of DatasetConstructors?
		[2] This should try and load from a raw_data file first rather than raw_data_year
		"""
		if verbose: print "[INFO]: Loading RAW [.dta] Files from: %s" % (self._source_dir)
		self.__raw_data 	= pd.DataFrame() 									
		for year in self.years:
			fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Loading Year: %s from file: %s" % (year, fn)
			self.__raw_data = self.__raw_data.append(pd.read_stata(fn))
		self.__raw_data = self.__raw_data.reset_index() 									#Otherwise Each year has repeated obs numbers
		del self.__raw_data['index'] 														#Remove Old Index

	def load_raw_from_hdf(self, years=[], verbose=True):
		"""
		Load HDF Version of RAW Dataset from a source_directory
		Note: 	To construct your own hdf version requires to initially load from NBER supplied RAW dta files
				Then use Constructor method ``convert_source_dta_to_hdf()``

		Notes
		-----
		[1] Move to Generic Class of DatasetConstructors?
		"""
		self.__raw_data 	= pd.DataFrame() 
		if years == [] or years == self._available_years: 						#years assigned prior to loading data
			fn = self._source_dir + self.__raw_data_hdf_fn
			if verbose: print "[INFO] Loading RAW DATA from %s" % fn
			self.__raw_data = pd.read_hdf(fn, key='raw_data')
		else:
			fn = self._source_dir + self.__raw_data_hdf_yearindex_fn 
			for year in years:
				if verbose: print "[INFO] Loading RAW DATA for year: %s from %s" % (year, fn)
				self.__raw_data = self.__raw_data.append(pd.read_hdf(fn, key='Y'+str(year)))

	def dataset_to_hdf(self, flname='default', key='default', format='table', verbose=True):
		"""
		Save a dataset to HDF File
		"""
		if flname == 'default':
			flname = self._name+'_%s-%s'%(self.years[0], self.years[-1])+'_SITC-L%s'%(self.level)+'_dataset.h5'
		if key == 'default':
			key = self._name
		if verbose: print "[INFO] Saving dataset to: %s" % flname
		self.dataset.to_hdf(flname, key='dataset', mode='w', complevel=9, complib='zlib', format=format)

	# ---------------------- #
	# - Supplementary Data - #
	# ---------------------- #

	def load_china_hongkongdata(self, years=[], return_dataset=False, verbose=True):
		"""
		Load China Kong Kong Adjustment Data into Supplementary Data with key ['chn_hk_adjust']
		
		Parameters
		----------
		years 			: 	Apply Year Filter
		return_dataset 	: 	Returns a reference to the data in supp_data dictionary

		File Pattern: 
		-------------
		CHINA_HK??.dta (?? = 88,89,...,00)

		Returns:
		-------
		self._supp_data['chn_hk_adjust'] 	:  	pd.DataFrame 	

		Future Work:
		-----------
			[1] Currently this method uses the source_dir that is defined when the object is initialised. 
				Could add in the option to specify a different source_dir but this probably won't get used. Not Wasting Time Now
			[2] Modify this so that only the intersection between available years and years. 
		"""
		# - Attributes of China Hong-Kong Adjustment - #
		fn_prefix 	= u'china_hk'
		fn_postfix 	= u'.dta'
		available_years = xrange(1988, 2000 + 1)
		key 		= u'chn_hk_adjust'
		#- Parse Year Filter - #
		if years == []:
			years = list(set([int(x) for x in self.years]).intersection(set(available_years))) 		#This will load the intersection of self.years and years available for adjustment
		else:
			years = list(set(years).intersection(set(available_years))) 	# Make sure years is supported by available data
		# - Import Data - #
		try: 
			self._supp_data[key]
			print "[NOTICE] It appears China Hong Kong Data has Already Been Imported!"
			return self._supp_data[key]
		except:
			data = pd.DataFrame()
			for year in years:
				if verbose: print "[INFO] Using source_dir: %s" % self._source_dir
				fn = self._source_dir + fn_prefix + str(year)[-2:] + fn_postfix
				if verbose: print "[INFO] Loading Year: %s from file: %s" % (year, fn)
				data = data.append(pd.read_stata(fn))
			# - Add Notes to the DataFrame - #
			data.notes = 	u'Files: ' + fn_prefix + u'??' + fn_postfix + '\n' 	+\
							u'Years: ' + str(years) + '\n' 						+\
							u'Source: ' + self._source_dir 
			# - Assign Data to Supp_Data with Key - #
			self._supp_data = {key : data}
		# - Option to Return Dataset - #
		if return_dataset:
			return self._supp_data[key]
			

	def bilateral_flows(self, verbose=False):
		"""
		Load NBERFeenstra Bilateral Trade Flows (summed across SITC commodities)

		File: 
		-----
		WTF_BILAT.dta

		Variables:
		---------
			ICode 		:	Importer country code
			ECode 		:	Exporter country code
			Importers 	: 	Importer country name
			Exporter 	: 	Exporter country name
			Value?? 	: 	Thousands of US dollars where ?? = 62, 63,...,00
		
		DataShape: Wide

		Notes:
		-----
		[1] Can use this Supplementary Data to check Aggregations and how different they are etc.
		[2] This corresponds to a CountryLevelExportSystem()
		
		"""
		fn = u'WTF_BILAT.dta'
		key = u'bilateral_flows'
		try:
			self._supp_data[key]
			print "[NOTICE] It appears Bilateral Flows Data has Already Been Imported!"
			return self._supp_data[key]
		except:
			if verbose: print "[INFO] Using source_dir: %s" % self._source_dir
			fn = self._source_dir + fn
			data = pd.read_stata(fn)
			# - Add Notes to the DataFrame - #
			data.notes = 	u'Source: ' + fn + '\n' + \
							u'Shape: Wide(bilateral pairs x years)' + '\n'
			# - Assign Data to supp_data - #
			self._supp_data[key] = data
			return self._supp_data[key]


	# ---------------------------------- #
	# - General Operations on Dataset  - #
	# ---------------------------------- #

	def reduce_to(self, to=['year', 'iiso3c', 'eiso3c', 'sitc4', 'value'], rtrn=False, verbose=False):
		"""
		Reduce a dataset to a specified list of columns

		Note
		----
		[1] This is an idea candidate for a constructor superclass so that it is inherited
		"""
		opstring = u"(reduce_to(to=%s))" % to
		if verbose: print "[INFO] Reducing Dataset from %s to %s" % (list(self.dataset.columns), to)
		self._dataset = self.dataset[to]
		self.operations += opstring
		if rtrn:
			return self.dataset

	def adjust_china_hongkongdata(self, verbose=False):
		"""
		Replace/Adjust China and Hong Kong Data to account for China Shipping via Hong Kong
		This will merge in the Hong Kong / China Adjustments provided with the dataset for the years 1988 to 2000.

		Note
		----
		[1] This method requires no operations to have been done previously on the dataset.  
		"""
		op_string = u'(adjust_raw_china_hongkongdata)'
		if check_operations(self, op_string): 							#Check if Operation has been conducted
				return None
		#-Merge Settings-#
		if self.operations != '':
			raise ValueError("This method requires no previous operations to have been performed on the dataset!")
		else:
		 	on 			= 	[u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'unit', u'dot'] 				#Merge on the Full complement of Items in the Original Dataset
		
		#-Note: Current merge_columns utility merges one column set at a time-#
		#-Values-#
		raw_value = self.dataset[on+['value']].rename(columns={'value' : 'value_raw'})
		try:
			supp_value = self._supp_data[u'chn_hk_adjust'][on+['value_adj']]
		except:
			raise ValueError("[ERROR] China/Hong Kong Data has not been loaded!")
		value = merge_columns(raw_value, supp_value, on, collapse_columns=('value_raw', 'value_adj', 'value'), dominant='right', output='final', verbose=verbose)

		# Note: Imposing the requirement that this be merged on complete matching information (i.e. no previous operations on the dataset, this section could be removed from try,except)
		#'Quantity' May not be available if collapse_to_valuesonly has been done etc.
		try:  															 
			#-Quantity-#
			raw_quantity = self._dataset[on+['quantity']]
			supp_quantity = self._supp_data[u'chn_hk_adjust'][on+['quantity']]
			quantity = merge_columns(raw_quantity, supp_quantity, on, collapse_columns=('quantity_x', 'quantity_y', 'quantity'), dominant='right', output='final', verbose=verbose)
			#-Join Values and Quantity-#
			if verbose: 
				print "[INFO] Merging Value Adjusted and Quantity Adjusted Series"
				print "[INFO] Value Adjusted Number of Observations: \t%s (Variables: %s)" % (value.shape[0], value.shape[1])
				print "[INFO] Quantity Adjusted Number of Observations: %s (Variables: %s)" % (quantity.shape[0], quantity.shape[1])
			updated_raw_values = value.merge(quantity, how='outer', on=on)
			if verbose:
				print "[INFO] Merged Number of Observations: \t\t%s (Variables: %s)" % (updated_raw_values.shape[0], updated_raw_values.shape[1])
		except:
			if verbose: print "[INFO] Quantity Information is not available in the current dataset\n"
			updated_raw_values = value 	#-Quantity Not Available-#

		report = 	u"[INFO] # of Observations in Original Dataset: %s\n" % (len(self._dataset)) +\
					u"[INFO] # of Observations in Updated Dataset: \t%s\n" % (len(updated_raw_values))
		if verbose: print report

		#-Cleanup of Temporary Objects-#
		del raw_value, supp_value, value
		try:
			del raw_quantity, supp_quantity, quantity
		except:
			pass 	#-Quantity Merge Hasn't Taken Place-#

		#- Add Notes -#
		update_operations(self, op_string)

		#-Set Dataset to the Update Values-#
		self._dataset = updated_raw_values
		

	def standardise_data(self, force=False, verbose=False):
		"""
		Run Appropriate Set of Standardisation over the Dataset
		
		Actions
		-------
			[1] Trade Values in $'s 
			[2] Add ISO3C Codes and Well Formatted CountryNames ('exportername', 'importername')
			[3] Marker for Standard SITC Revision 2 Codes

		Notes
		-----
		[1] Raw Dataset has Non-Standard SITC rev2 Codes so adding a marker to identify 'official' codes

		Future Work
		-----------
		[1] Remove this and use subfunctions in __init__ to be more explicit?
		[2] Is this needed? Delete?
		"""
		op_string = u"(standardise_data)"
		#-Check if Operation has been conducted-#
		if check_operations(self, op_string): return None
		#-Core-#
		self.change_value_units(verbose=verbose) 			#Change Units to $'s
		self.add_iso3c(verbose=verbose)
		self.add_isocountrynames(verbose=verbose)
		self.add_sitcr2_official_marker(verbose=verbose) 	#Build SITCR2 Marker
		#- Add Operation to df attribute -#
		update_operations(self, op_string)


	# ------------------------------- #
	# - Operations on Country Codes - #
	# ------------------------------- #

	#Move These to Meta Data#

	fix_exporter_to_iso3n = 	{
									'Asia NES' 	: 896,
									'Italy'		: 381,
									'Norway' 	: 579,
									'Switz.Liecht' : 757,
									'Samoa'		: 882,
									'Taiwan'	: 158,
									'USA' 		: 842,
								}

	fix_ecode_to_iso3n = 		{ 										
									'450000' 	: 896,
									'533800'	: 381,
									'555780' 	: 579,
									'557560' 	: 757,
									'728882'	: 882,
									'458960'	: 158,
									'218400' 	: 842,
								}
	# Checked With: 
	# df = a.raw_data
	# df.loc[df.exporter==<item from fix_exporter_to_iso3n>].ecode.unique()


	fix_exporter_to_iso3c = 	{
									'Asia NES' 	: '.',
									'Italy' 	: 'ITL',
									'Norway'	: 'NOR',
									'Switz.Liecht' : 'CHE',
									'Samoa'		: 'WSM',
									'Taiwan'	: 'TWN',		#Note this is also 480 (Other Asia, NES)
									'USA' 		: 'USA',
								}

	# Note: These are technically duplicates, but does it help to keep the logic separable?

	fix_importer_to_iso3n = 	{ 
									'Asia NES' 	: 896,
									'Italy'		: 381,
									'Norway' 	: 579,
									'Samoa'		: 882,
									'Switz.Liecht' : 757,
									'Taiwan'	: 158,
									'USA' 		: 842,
								}

	fix_icode_to_iso3n = 		{ 
									'450000' 	: 896,
									'533800'	: 381,
									'555780' 	: 579,
									'728882'	: 882,
									'557560' 	: 757,
									'458960'	: 158,
									'218400' 	: 842,
								}
	# Checked With: 
	# df = a.raw_data
	# df.loc[df.importer==<item from fix_importer_to_iso3n>].icode.unique()

	fix_importer_to_iso3c = 	{
									'Asia NES' 	: '.',
									'Italy' 	: 'ITL',
									'Norway'	: 'NOR',
									'Samoa'		: 'WSM',
									'Switz.Liecht' : 'CHE',
									'Taiwan'	: 'TWN',
									'USA' 		: 'USA',

								}

	@property 
	def fix_countryname_to_iso3n(self):
		""" 
		Compute a joint dictionary of exporter and importer adjustments
		Usage: A joint dictionary can reduce errors by ensuring both exporters and importers are encoded the same way
		"""
		try:
			return self.__fix_countryname_to_iso3n
		except:
			#-Load Data-#
			fix_exporter_to_iso3n = self.fix_exporter_to_iso3n
			fix_importer_to_iso3n = self.fix_importer_to_iso3n
			#-Core-#
			countryname_to_iso3n = dict()
			for key in fix_exporter_to_iso3n.keys():
				countryname_to_iso3n[key] = fix_exporter_to_iso3n[key]
			for key in fix_importer_to_iso3n.keys():
				try:
					if countryname_to_iso3n[key] == fix_importer_to_iso3n[key]:
						pass
					else:
						raise ValueError("The index: %s conflicts between exporter and importer fix dictionaries\nExporter: %s != Importer: %s") % (key, fix_exporter_to_iso3n[key], fix_importer_to_iso3n[key])
				except:
					countryname_to_iso3n[key] = fix_importer_to_iso3n[key]
			self.__fix_countryname_to_iso3n = countryname_to_iso3n
			return countryname_to_iso3n

	def split_countrycodes(self, dataset=True, apply_fixes=True, iso3n_only=False, force=False, verbose=True):
		"""
		Split CountryCodes into components ('icode', 'ecode')
		XXYYYZ => UN-REGION [2] + ISO3N [3] + Modifier [1]

		dataset 			: True/False [The only function that can act on RAW DATA]
		apply_fixes 		: adjusts iso3n numbers to match updated codes. 
		iso3n_only 			: Removes iregion and imod
		force 				: force this to run regardless of op_string

		Notes
		-----
		[1] Should this be done more efficiently? (i.e. over a single pass of the data) 
			Current timeit result: 975ms per loop for 1 year
		"""
		#-Set Data from Dataset OR Raw Data-#
		if dataset:
			data = self.dataset
		else:
			data = self.raw_data
		#-Check if Operation has been conducted-#
		op_string = u"(split_countrycodes)"
		if check_operations(self, op_string, verbose=verbose): 
			if force: 	
				pass
			else:
				return None
		# - Importers - #
		if verbose: print "Spliting icode into (iregion, iiso3n, imod)"
		data['iregion'] = data['icode'].apply(lambda x: int(x[:2]))
		data['iiso3n']  = data['icode'].apply(lambda x: int(x[2:5]))
		data['imod'] 	= data['icode'].apply(lambda x: int(x[-1]))
		# - Exporters - #
		if verbose: print "Spliting ecode into (eregion, eiso3n, emod)"
		data['eregion'] = data['ecode'].apply(lambda x: int(x[:2]))
		data['eiso3n']  = data['ecode'].apply(lambda x: int(x[2:5]))
		data['emod'] 	= data['ecode'].apply(lambda x: int(x[-1]))
		#- Add Operation to df attribute -#
		update_operations(self, op_string)
		if not dataset:
			return None
		#-Apply Custom Fixes and ISO3N Option-#
		if iso3n_only:
			del data['iregion']
			del data['imod']
			del data['eregion']
			del data['emod']
		if apply_fixes:
			self.apply_iso3n_custom_fixes(match_on='countrycode', verbose=verbose)
		

	def apply_iso3n_custom_fixes(self, match_on='countrycode', verbose=True):
		""" 
		Apply Custom Fixes for ISO3N Numbers
		
		match_on 	: allows matching on 'countryname' (i.e. exporter, importer) or 'countrycode' (i.e. ecode, icode)

		Note
		----
		[1] Currently uses attribute fix_countryname_to_iso3n, fix_icode_to_iso3n, fix_ecode_to_iso3n (will move to meta)

		Future Work 
		-----------
		[1] Write Tests
		"""
		#-Op String-#
		op_string = u"(apply_iso3n_custom_fixes)"
		if check_operations(self, op_string): 
			return None
		if not check_operations(self, u"(split_countrycodes)", verbose=verbose): 		#ensure iiso3n, eiso3n are constructed
			if verbose: print "[INFO] Calling split_countrycodes() method"
			self.split_countrycodes(apply_fixes=False, iso3n_only=True, verbose=verbose)
		#-Core-#
		if match_on == 'countryname':
			fix_countryname_to_iso3n = self.fix_countryname_to_iso3n
			for key in sorted(fix_countryname_to_iso3n.keys()):
				if verbose: print "For countryname %s updating iiso3n and eiso3n codes to %s" % (key, fix_countryname_to_iso3n[key])
				df = self._dataset
				df.loc[df.importer == key, 'iiso3n'] = fix_countryname_to_iso3n[key]
				df.loc[df.exporter == key, 'eiso3n'] = fix_countryname_to_iso3n[key]
		elif match_on == 'countrycode':
			fix_ecode_to_iso3n = self.fix_ecode_to_iso3n 														#Will be moved to Meta
			for key in sorted(fix_ecode_to_iso3n.keys()):
				if verbose: print "For ecode %s updating eiso3n codes to %s" % (key, fix_ecode_to_iso3n[key])
				df = self._dataset
				df.loc[df.ecode == key, 'eiso3n'] = fix_ecode_to_iso3n[key]
			fix_icode_to_iso3n = self.fix_icode_to_iso3n 														#Will be moved to Meta
			for key in sorted(fix_icode_to_iso3n.keys()):
				if verbose: print "For icode %s updating iiso3n codes to %s" % (key, fix_icode_to_iso3n[key])
				df = self._dataset
				df.loc[df.icode == key, 'iiso3n'] = fix_icode_to_iso3n[key]
		else:
			raise ValueError("match_on must be either 'countryname' or 'countrycode'")
		#- Add Operation to class attribute -#
		update_operations(self, op_string)

	def add_iso3c(self, verbose=False):
		""" 
		Add ISO3C codes to dataset

		This method uses the iso3n codes embedded in icode and ecode to add in iso3c codes
		I find this to be the most reliable matching method. 
		However there are other ways by matching on countrynames etc.
		Some of these concordances can be found in './meta'

		Alternatives
		------------
		[1] build_countrynameconcord_add_iso3ciso3n()

		Requires
		--------
		[1] split_countrycodes()
		[2] iso3n_to_iso3c (#Check if Manual Adjustments are Required: nberfeenstrawtf(iso3n)_to_iso3c_adjust)

		Notes
		-----
		[1] This matches all UN iso3n codes which aren't just a collection of countries. 
			For example, this concordance includes items such as 'WLD' for World
		[2] Should cleanup of iso3n and iregion imod occur here? Should this collapse (sum)?
		"""
		#-OpString-#
		op_string = u"(add_iso3c)"
		if check_operations(self, op_string): return None
		#-Core-#
		if not check_operations(self, u"(split_countrycodes)"): 		#Requires iiso3n, eiso3n
			if verbose: print "[INFO] Calling split_countrycodes() method"
			self.split_countrycodes(apply_fixes=True, iso3n_only=True, verbose=verbose)
		un_iso3n_to_iso3c = iso3n_to_iso3c(source_institution='un')
		#-Concord and Add a Column-#
		self._dataset['iiso3c'] = self._dataset['iiso3n'].apply(lambda x: concord_data(un_iso3n_to_iso3c, x, issue_error='.'))
		self._dataset['eiso3c'] = self._dataset['eiso3n'].apply(lambda x: concord_data(un_iso3n_to_iso3c, x, issue_error='.'))
		#- Add Operation to cls attribute -#
		update_operations(self, op_string)

	def add_isocountrynames(self, source_institution='un', verbose=False):
		"""
		Add Standard Country Names

		source_institution 	:	Allows to specify which institution data to use in the match between iso3n and countryname
								[Default: 'un']

		Requires
		--------
		[1] split_countrycodes()
		[2] iso3n_to_iso3c (#Check if Manual Adjustments are Required: nberfeenstrawtf(iso3n)_to_iso3c_adjust)

		Notes
		-----
		[1] This matches all UN iso3n codes which aren't all countries. 
			These include items such as 'WLD' for World
		"""
		#-OpString-#
		op_string = u"(add_isocountrynames)"
		if check_operations(self, op_string): return None
		#-Checks-#
		if not check_operations(self, u"(split_countrycodes"): 		#Requires iiso3n, eiso3n
			self.split_countrycodes(apply_fixes=True, iso3n_only=True, verbose=verbose)
		#-Core-#
		un_iso3n_to_un_name = iso3n_to_name(source_institution=source_institution) 
		#-Concord and Add a Column-#
		self._dataset['icountryname'] = self._dataset['iiso3n'].apply(lambda x: concord_data(un_iso3n_to_un_name, x, issue_error='.'))
		self._dataset['ecountryname'] = self._dataset['eiso3n'].apply(lambda x: concord_data(un_iso3n_to_un_name, x, issue_error='.'))

		#-OpString-#
		update_operations(self, op_string)

	def countries_only(self, error_code='.', rtrn=False, verbose=True):
		"""
		Filter Dataset for Countries Only AND returns a reference to dataset attribute

		Requires
		--------
		[1] add_iso3c()

		Note
		----
		[1] This uses the iso3c codes to filter on countries only
		[2] Write Tests to check the sum of a countries exports and compare to Corresponding World Export Line
		[3] Build a Report for Dropped countrycodes
		[4] This leaves in old countries that may no longer currently exist!

		Future Work
		-----------
		[1] Rewrite these to use .loc method?
		"""
		#-OpString-#
		op_string = u"(countries_only)"
		if check_operations(self, op_string): return self.dataset 			#Already been computed
		#-Checks-#
		if not check_operations(self, u"(add_iso3c)"): 			
			if verbose: print "[INFO] Calling add_iso3c method"
			self.add_iso3c(verbose=verbose)
		#-Drop NES and Unmatched Countries-#
		self._dataset = self.dataset[self.dataset.iiso3c != error_code] 	#Keep iiso3n Countries
		self._dataset = self.dataset[self.dataset.eiso3c != error_code]		#Keep eiso3n Countries
		#-Drop WLD-#
		self._dataset = self.dataset[self.dataset.iiso3c != 'WLD']
		self._dataset = self.dataset[self.dataset.eiso3c != 'WLD']
		#-Drop '.'-#
		self._dataset = self.dataset[self.dataset.iiso3c != '.']
		self._dataset = self.dataset[self.dataset.eiso3c != '.']
		#-ResetIndex-#
		self._dataset = self._dataset.reset_index() 						
		#-OpString-#
		update_operations(self, op_string)
		if rtrn: 															#If return dataset, return with old observation numbers
			return self.dataset
		del self._dataset['index'] 											#This Removes old index number.
		

	def drop_world_observations(self, verbose=True):
		"""
		Drop Observations that contain 'World' in either exporter or importer
		"""
		#-OpString-#
		op_string = u"(drop_world_observations)"
		if check_operations(self, op_string): 
			return None 			#Already been computed
		#-Core-#
		if verbose: print "[INFO] Dropping Observations that include `World` in importer or exporter attribute"
		df = self.dataset
		df = df.loc[(df.importer != "World") & (df.exporter != "World")]
		self._dataset = df


	def world_only(self, error_code='.', rtrn=False, verbose=True):
		"""
		Filter Dataset for World Exports Only and returns a reference to the dataset attribute

		Requires
		--------
		[1] add_iso3c()

		Future Work
		-----------
		[1] Build a Report
		[1] Add inplace option to return a dataframe rather than right to dataset?
		"""
		#-OpString-#
		op_string = u"(world_only)"
		if check_operations(self, op_string): return self.dataset 	#Already been computed
		#-Checks-#
		if not check_operations(self, u"(add_iso3c)"): 			#Requires iiso3n, eiso3n
			self.add_iso3c(verbose=verbose)
		#-Core-#
		self._dataset = self._dataset.loc[(self._dataset.iiso3c == 'WLD') | (self._dataset.eiso3c == 'WLD')] 			#Take WLD either in iiso3c or eiso3c (| = or)
		#-OpString-#	
		update_operations(self, op_string)
		if rtrn:
			return self.dataset


	def adjust_countrycodes_intertemporal(self, force=False, dropvars=['icode', 'importer', 'ecode', 'exporter', 'iiso3n', 'eiso3n'], verbose=True):
		"""
		Adjust Country Codes to be Inter-temporally Consistent

		Future Work
		-----------
		[1] Write Tests
		[2] Make the Reporting More Informative
		"""
		from pyeconlab.trade.dataset.NBERWTF.meta import iso3c_recodes_for_1962_2000
		from pyeconlab.util import concord_data

		#-Parse Complete Dataset Check-#
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("This is not a complete Dataset! ... use force=True if you want to proceed.")
		#-OpString-#
		op_string = u"(adjust_countrycodes_intertemporal)"
		if check_operations(self, op_string): 
			return None
		#-Checks-#
		if not check_operations(self, u"(countries_only)"): 	   	#Adds iso3c	
			if verbose: print "[INFO] Calling countries_only method to remove NES and World aggregations from the dataset"
			self.countries_only(verbose=verbose)
		#-Adjust Codes-#
		if verbose: print "[INFO] Adjusting Codes for Intertemporal Consistency from meta subpackage (iso3c_recodes_for_1962_2000)"
		self._dataset['iiso3c'] = self.dataset['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
		self._dataset['eiso3c'] = self.dataset['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
		#-Drop Removals-#
		if verbose: print "[INFO] Deleting Recodes to '.'"
		self._dataset = self.dataset[self.dataset['iiso3c'] != '.']
		self._dataset = self.dataset[self.dataset['eiso3c'] != '.']
		#-Collapse Constructed Duplicates-#
		subidx = set(self.dataset.columns)
		subidx.remove('value')
		for item in ['quantity', 'unit', 'dot'] + dropvars:
			try:
				subidx.remove(item)
			except:
				pass
		if verbose: print "[INFO] Collapsing Dataset to SUM duplicate entries on %s" % list(subidx)
		self._dataset = self.dataset[list(subidx) + ['value']].groupby(list(subidx)).sum()
			#self._dataset = self.dataset.groupby(list(['year', 'iiso3c', 'eiso3c', 'sitc%s' % self.level])).sum()
			#self._dataset = self.dataset.sort(columns=['year', 'iiso3c', 'eiso3c', 'sitc%s' % self.level])
		self._dataset = self.dataset.reset_index() 													#Return Flat File															
		#-OpString-#	
		update_operations(self, op_string)


	def countryname_concordance_using_cc(self, concord_vars=('countryname', 'iso3c'), target_dir=None, force=False, verbose=False):
		"""
		Compute a Country Name Concordance using package: pycountrycode
		
		Returns:
		--------
		pd.DataFrame(countryname,iso3c,iso3n) and/or writes a file
		 	
		Dependencies:
		-------------
		[1] PyCountryCode [https://github.com/vincentarelbundock/pycountrycode]
			Note: pycountrycode has an issue with converting iso3n to iso3c so currently use country names
			vincentarelbundock/pycountrycode Issue #24

		Notes
		-----
		[1] It is better to use ISO3N Codes that are built into icode and ecode
			Therefore STOP work on this approach.
			Current Concordances can be found in "./meta"

		Future Work:
		------------
		[1] Build my own version of pycountrycode so that this work is internalised to this package and doesn't depend on PyCountryCode
			I would like Time Varying Definitions of Country Codes, In addition to Time Varying Aggregates like LDC, MDC, etc.
		[2] Add Option to Write Concordance to a py file or csv etc
		[3] Write Some Error Checking tests
		[4] Turn this Routine into a utility function and remove code duplication
		"""
		#-Parse Complete Dataset Check-#
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("This is not a complete Dataset!\n If you want to build a concordance for a given year use force=True")
		iso3c = cc.countrycode(codes=self.country_list, origin='country_name', target='iso3c')
		#-Reject Non-String Responses-#
		for idx,code in enumerate(iso3c):
			if type(code) != str:
				iso3c[idx] = '.' 																	#encode as '.' missing
		#-Check Same Length-# 																		#This is probably redundant as zip will complain?
		if len(iso3c) != len(self.country_list):
			raise ValueError("Results != Length of Original Country List")
		concord = pd.DataFrame(zip(self.country_list, iso3c), columns=['countryname', 'iso3c'])
		concord['iso3c'] = concord['iso3c'].apply(lambda x: '.' if len(x)!=3 else x)
		concord['iso3n'] = cc.countrycode(codes=concord.iso3c, origin='iso3c', target='iso3n')
		concord.name = 'Concordance for %s : %s' % (self._name, concord.columns)
		self.country_concordance = concord
		#-Parse File Option-#
		if type(target_dir) == str:
			target_dir = check_directory(target_dir)
			fl = "%s_to_%s.py" % (concord_vars[0], concord_vars[1]) 					#Convention from_to_to
			if verbose: print "[INFO] Writing concordance to: %s" % (target_dir + fl)
			concord_series = concord[list(concord_vars)].set_index(concord_vars[0])[concord_vars[1]] 	#Get Indexed Series Index : Value#
			concord_series.name = u"%s to %s" % (concord_vars[0], concord_vars[1])
			docstring 	= 	u"Concordance for %s to %s\n" % (concord_vars) 			+ \
							u"%s" % self
			from_idxseries_to_pydict(concord_series, target_dir=target_dir, fl=fl, docstring=docstring, verbose=False)
		return self.country_concordance


	# ------------------------------- #	
	# - Operations on Product Codes - #
 	# ------------------------------- #	

	def collapse_to_valuesonly(self, subidx=None, return_duplicates=False, verbose=False):
		"""
		Adjust Dataset For Export Values that are defined multiple times due to Quantity Unit Codes ('unit')
		Note: This will remove 'quantity', 'unit' ('dot'?)

		Questions
		---------
		1. Does this need to be performed before adjust_china_hongkongdata (as this might match multiple times!)?
		2. Write Tests

		"""
		#-Find Appropriate idx-#
		if type(subidx) != list:
			subidx = set(self.dataset.columns)
			for item in ['quantity', 'unit', 'dot']: 	#Cannot Aggregate These Items
				try:
					subidx.remove(item)
				except:
					pass
			subidx.remove('value')						#Remove to Aggregate in groupby
			subidx = list(subidx) 						
		#-Check if Operation has been conducted-#
		op_string = u"(collapse_to_valuesonly[%s])" % subidx
		if check_operations(self, op_string): return None
		# - Conduct Duplicate Analysis - #
		dup = self._dataset.duplicated(subset=subidx)  
		if verbose:
			print "[INFO] Current Dataset Length: %s" % self._dataset.shape[0]
			print "[INFO] Current Number of Duplicate Entry's: %s" % len(dup[dup==True])
			print "[INFO] Deleted 'quantity', 'unit' as cannot aggregate quantity data in different units and 'dot' due to the existence of np.nan"
		if return_duplicates: 			#Return Duplicate Rows
			dup = self.dataset[dup]
		#-Collapse/Sum Duplicates-#
		self._dataset = self.dataset[subidx+['value']].groupby(by=subidx).sum()
		self._dataset = self.dataset.reset_index() 									#Remove IDX For Later Data Operations
		if verbose:
			print "[INFO] New Dataset Length: %s" % self._dataset.shape[0]
		#- Add Operation to df attribute -#
		update_operations(self, op_string)
		if return_duplicates:
			return dup

	def change_value_units(self, verbose=False):
		""" 
		Updates Values to $'s instead of 1000's of $'s' in Dataset
		"""
		#-OpString-#
		op_string = u"(change_value_units)"
		if check_operations(self, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Setting Values to be in $'s not %s$'s" % (self._raw_units)
		self._dataset['value'] = self.dataset['value'] * self._raw_units
		#-OpString-#
		update_operations(self, op_string)

	def add_sitcr2_official_marker(self, level=4, source_institution='un', verbose=False):
		""" 
		Add an Official SITCR2 Marker to Dataset
		source_institution 	: 	allows to specify where SITC() retrieves data [Default: 'un']
		"""
		#-OpString-#
		op_string = u"(add_sitcr2_official_marker)"
		if check_operations(self, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Adding SITC Revision 2 (Source='un') marker variable 'SITCR2'"
		sitc = SITC(revision=2, source_institution=source_institution)
		codes = sitc.get_codes(level=level)
		sitcl = 'sitc%s' % level
		self._dataset['SITCR2'] = self.dataset[sitcl].apply(lambda x: 1 if x in codes else 0)
		#-OpString-#
		update_operations(self, op_string)

	def add_productcode_levels(self, verbose=False):
		"""
		Add SITC L1, L2, and L3 Codes derived from 'sitc4'
		"""
		for level in [1,2,3]:
			self.add_productcode_level(level, verbose)

	def add_productcode_level(self, level, verbose=False):
		"""
		Add a Product Code for a specified level between 1 and 3 for 'sitc4'

		Note
		----
		[1] This could be simplified by using sitcl = 'sitc%s' % level string 
		"""
		if level == 1:
			op_string = u"(add_productcode_level1)"
			if check_operations(self, op_string): return None
		elif level == 2:
			op_string = u"(add_productcode_level2)"
			if check_operations(self, op_string): return None
		elif level == 3:
			op_string = u"(add_productcode_level3)"
			if check_operations(self, op_string): return None
		else:
			raise ValueError("SITC4 Can Only Be Split into Levels 1,2, or 3")
		#-Core-#
		if verbose: print "[INFO] Adding Product Code Level: SITC L%s" % level
		if level == 1:
			self._dataset['SITCL1'] = self._dataset['sitc4'].apply(lambda x: x[0:1])
		if level == 2:
			self._dataset['SITCL2'] = self._dataset['sitc4'].apply(lambda x: x[0:2])
		if level == 3:
			self._dataset['SITCL3'] = self._dataset['sitc4'].apply(lambda x: x[0:3])
		#-OpString-#
		update_operations(self, op_string)

	def collapse_to_productcode_level(self, level=3, subidx='default', verbose=False):
		"""
		Collapse the Dataset to a Higher Level of Aggregation 

		level 	: 	[1,2,3]
					Default: 3
		subidx 	: 	Specify a Column Filter
					[Default: Builds a SubIDX from self.dataset.columns]
					Alternatives: 	['year', 'icode', 'importer', 'ecode', 'exporter', 'sitc4', 'dot', 'value']
									['year', 'iiso3c', 'eiso3c', 'sitc4', 'value']

		Note
		----
		[1] This is a good candidate to be in a superclass
		[2] Why restrict to the default subidx?

		Future Work
		-----------
		[1] Infer the level and then aggregate based on that inference rather than relying on sitc4 data as the baseline. 
		"""
		if verbose: print "[INFO] Cannot Aggregate Quantity due to units. Discarding 'quantity'"
		op_string = u"(collapse_to_productcode_level%s)" % level
		if check_operations(self, op_string): 
			return None
		if level not in [1,2,3]:
			raise ValueError("Level must be 1,2, or 3 for SITC4 Data")
		if subidx == 'default':
			cols = set(self.dataset.columns)
			for item in ['quantity', 'unit', 'dot']:
				try:
					cols.remove(item)
				except:
					pass 																#Item not in dataset, report?
			#-Ensure 'value' is last-#
			cols.remove('value')
			subidx = list(cols) + ['value'] 										#Is this really necessary? just remove value?
		if verbose: print "[INFO] Collapsing Data to SITC Level #%s" % level
		colcode = 'sitc%s' % level
		self._dataset[colcode] = self.dataset['sitc4'].apply(lambda x: x[0:level])
		#-Aggregate-#
		for idx,item in enumerate(subidx):
			if item == 'sitc4': subidx[idx] = colcode 								# Remove sitc4 and add in the lower level of aggregation sitc3 etc.
		if verbose: print "[INFO] Aggregating on: %s" % subidx[:-1]
		self._dataset = self.dataset[subidx].groupby(by=subidx[:-1]).sum() 		# Exclude 'value', as want to sum over it. It needs to be last in the list!
		self._dataset = self.dataset.reset_index()
		self.level = level
		#-OpString-#
		update_operations(self, op_string)

	def delete_sitc4_issues_with_raw_data(self, verbose=False):
		"""
		This method deletes any known issues with the raw_data associated with productcodes

		Requirements
		------------
		self.level == 4

		Notes
		-----
		[1] SITC4 Deletions is Documented in meta subpackage

		"""
		from .meta import sitc4_deletions
		self.sitc4_deletions = sitc4_deletions 									#Add as an Attribute
		#-Parse Requirement-#
		if self.level != 4:
			raise ValueError("The Dataset must be using SITC level 4 Data")
		#-Core-#
		sobs = self.dataset.shape[0]
		if verbose: print "[INFO] Starting Dataset has %s observations" % sobs
		for item in self.sitc4_deletions + ['','.']: 															#Delete Error Items '.' and empty items ''
			sgobs = self.dataset[self.dataset['sitc4'] == item].shape[0]
			if verbose: print "[INFO] Deleting sitc4 productcode: %s [Dropping %s observations]" % (item, sgobs)
			self._dataset = self.dataset[self.dataset['sitc4'] != item]
		if verbose: print "[INFO] Dataset now has %s observations [%s Deleted]" % (self.dataset.shape[0], sobs - self.dataset.shape[0])

 	def identify_alpha_productcodes(self, verbose=False):
		"""
		Identify Productcodes that contain an alpha code 'A', 'X'

		'X' : 	Adjustments for aggregation mismatch between Levels 
				4441 + 4442 = $150
				444 		= $200
				444X		= $50

		'A' : 	No disaggregated details reported, but there are values at higher levels of aggregation 
				444 	= $200 but no 4441 or 4442 defined then 
				444A 	= $200 

		Note
		----
		[1] The A and X codes are not used for the adjusted SITC codes of the 35 countries for
		which specific corrections and adjustments were made, as described in Section 5.

		[1] To obtain comparable inter-temporal codes requires adjustments to the data. A concordance is required
		to bring the specially constructed product codes to data in future years.

		"""
		op_string = u"(add_productcode_alpha_indicator)"
		if check_operations(self, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Identifying SITC Codes with A and X"
		self._dataset['SITCA'] = self._dataset['sitc%s' % self.level].apply(lambda x: 1 if re.search("[aA]",x) else 0)
 		self._dataset['SITCX'] = self._dataset['sitc%s' % self.level].apply(lambda x: 1 if re.search("[xX]",x) else 0)
		#-OpString-#
		update_operations(self, op_string)

	def drop_alpha_productcodes(self, cleanup=True, verbose=False):
		"""
		Drop Productcodes that contain an alpha code 'A', 'X'

		Note
		----
		[1] The A and X codes are not used for the adjusted SITC codes of the 35 countries for
		which specific corrections and adjustments were made, as described in Section 5.

		[1] To obtain comparable inter-temporal codes requires adjustments to the data. A concordance is required
		to bring the specially constructed product codes to data in future years.
		"""
		op_string = u"(drop_alpha_productcodes)"
		if check_operations(self, op_string): return None
		#-Core-#
		if not check_operations(self, u"(identify_alpha_productcodes)"):
			self.identify_alpha_productcodes(verbose=verbose)
		if verbose: print "[INFO] Dropping SITC Codes with A and X"
		obs = self.dataset.shape[0]
		df = self.dataset
		df = df.loc[(df.SITCA != 1) & (df.SITCX != 1)]
		self._dataset = df
		if verbose: print "[INFO] Dropped %s Observations" % (obs - self.dataset.shape[0])
		#-OpString-#
		update_operations(self, op_string)
		if cleanup:
			if verbose: print "[INFO] Cleaning up SITC A and X Identifiers"
			del self._dataset['SITCA']
			del self._dataset['SITCX']

	def compute_valAX_sitclevel(self, level=3):
		""" 
		Compute the Value of Codes that Contain AX and the percentage of that Groups Value based on an aggregated level

		level 	: 	specify a higher level of aggregation [0,1,2,3]
					[Default: 3]

		Required Columns: 'SITC#' #=[1,2,3]; 'year', 'value'

		Notes
		-----
		[1] At the SITCL3 the maximum value contained in AX codes is 4% (mean: 0.2%)
			There isn't a huge loss of data by deleting them. These values should be included in the SITCL3 Dataset
		[2] Should I unstack 'year'
		"""
		#-Required Items-#
		self.add_iso3c() 															# ISO3C
		self.add_productcode_levels() 												# SITCL3
		self.identify_alpha_productcodes()											# SITCA, SITCX
		#-Data-#
		sitcl = 'SITCL%s' % level
		data = self.dataset.copy(deep=True)
		data['SITC_AX'] = data['SITCA'] + data['SITCX']
		data['SITC_AX'] = data['SITC_AX'].apply(lambda x: 1 if x >= 1 else 0)
		if sitcl == 'SITCL0':
			subidx = ['year', 'SITC_AX', 'value']
			data = data[subidx].groupby(['year', 'SITC_AX']).sum()
		else:
			subidx = ['year', sitcl, 'SITC_AX', 'value']
			data = data[subidx].groupby(['year', sitcl, 'SITC_AX']).sum()
		data = data.unstack(level='SITC_AX')
		data.columns = data.columns.droplevel()
		data.columns = pd.Index(['NOAX', 'AX'])
		data['%Tot'] = data['AX'].div(data['NOAX'] + data['AX']) * 100
		return data

	def compute_val_unofficialcodes_sitclevel(self, level=3, includeAX=False):
		""" 
		Compute the Value of Codes that are Unofficial and the percentage of that Groups Value based on an aggregated level

		level 	: 	specify a higher level of aggregation [0,1,2,3]
					[Default: 3]

		Future Work
		-----------
		[1] Implement the case level = 0
			# if sitcl == 'SITCL0':
			# 	subidx = ['year', 'AX', 'value']
			# 	data = data[subidx].groupby(['year', 'MARKER']).sum()
			# else:
		"""
		#-RequiredItems-#
		#self.add_iso3c()
		self.add_productcode_levels() 												# SITCL3
		self.add_sitcr2_official_marker(source_institution='un')					# SITCR2
		if includeAX:
			self.identify_alpha_productcodes()										# SITCA, SITCX
		#-Data-#
		sitcl = 'SITCL%s' % level
		data = self.dataset.copy(deep=True)
		if includeAX:
			data['AX'] = data['SITCA'] + data['SITCX'] 								#A or X
			data['AX'] = data['AX'].apply(lambda x: 1 if x >= 1 else 0)
			subidx = ['year', sitcl, 'AX', 'SITCR2', 'value']
			data = data[subidx].groupby(['year', sitcl, 'AX', 'SITCR2']).sum()
			data = data.unstack(level=['AX', 'SITCR2'])
			data.columns = data.columns.droplevel()
			midx = pd.MultiIndex.from_tuples([(0,1)], names=['AX', 'SITCR2']) 					
			s1 	= data[[(0,1)]].div(pd.DataFrame(data.sum(axis=1), columns=midx)) * 100
			s1.columns = ['%Official']
			midx = pd.MultiIndex.from_tuples([(1,0)], names=['AX', 'SITCR2'])
			s2 	= data[[(1,0)]].div(pd.DataFrame(data.sum(axis=1), columns=midx)) * 100
			s2.columns = ['%AX'] 									
			s3 	= pd.DataFrame(data[[(0,0), (1,0)]].sum(axis=1).div(data.sum(axis=1)) * 100, columns=['%NotOffandAX'])
			for item in [s1,s2,s3]:
				data = data.merge(item, left_index=True, right_index=True)
			data.columns = ['NotAX-NotSITCR2', 'NotAX-SITCR2', 'AX-NotSITCR2'] + list(data.columns[3:])
			data = data.stack().unstack(level='year')
			return data
		else:
			subidx = ['year', sitcl, 'SITCR2', 'value']
			data = data[subidx].groupby(['year', sitcl, 'SITCR2']).sum()
			data = data.unstack(level='SITCR2')
			data.columns = data.columns.droplevel()
			data.columns = pd.Index(['SITCR2', 'NOT-SITCR2'])
			data['%Tot'] = data['NOT-SITCR2'].div(data['SITCR2'] + data['NOT-SITCR2']) * 100
			data = data.stack.unstack(level='year')
		return data


	def intertemporal_consistent_productcodes(self, verbose=False):
		""" 
		Construct a set of ProductCodes that are Inter-temporally Consistent based around SITC Revision 2

		Full TimeFrames
		===============

		Dataset #1 [1962 to 2000]
		-------------------------

			The longest time horizon in the dataset. 
			Need to aggregate a lot of Product Codes to Level 3 + 0 to allow for dynamic consistency
		
		Dataset #2 [1962 to 2000] [SITCR2L3]
		-------------------------------------

			Aggregate ALL Codes to SITCR2 Level 3 
			This brings in the vast majority of data and Level4 'Corrections'
			Easy to Construct

			**Current Focus** [See meta data for reasons]

		Subset TimeFrames
		=================

		Dataset #3 [1974 to 2000]
		-------------------------

			A lot of SITCR2 Codes get introduced into the dataset in 1974. 
			Starting from 1974 would allow a greater diversity of products but removes 10 years of dynamics

			TBD		

		Dataset #4 [1984 to 2000]
		-------------------------

			A lot of SITCR2 Codes get introduced into the dataset in 1984. 
			Starting from 1984 would allow a greater diversity of products but removes 10 years of dynamics

			TBD	

		"""
		#-List of Codes to DROP-#
		# See: .delete_sitc4_issues_with_raw_data()

		### -- Working Here --- ###
		
		raise NotImplementedError

	def intertemporal_consistent_productcodes_concord(self, verbose=False):
		"""
		Produce a concordance for inter-temporal consistent product codes for converting data post year 2000

		SITCR2 to CONCORD
		"""
		# ---------------- #
		# - Working Here - #
		# ---------------- #

		raise NotImplementedError


	# ----------------------- #
	# - Construct Datasets  - #
	# ----------------------- #

	dataset_description 	= { 
		'CNTRY_SR2L3_Y62to00_A'  	:  'DescriptionHere'
	}

	def construct_dataset(self, dataset, verbose=False):
		""" 
		Construct Datasets
		==================
		
		A Wrapper for Returning Predefined Datasets

		SITCL4 Datasets
		===============

		IN-WORK

		SITCL3 Datasets
		===============
		Basic Cleaned Datasets 
		----------------------
		Method: construct_dataset_SC_CNTRY_SR2L3_Y62to00_A to _D
		
		Trade
		~~~~~ 
		[BaTr_SITC3_A] data='trade', dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False
		[BaTr_SITC3_B] data='trade', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False
		
		Exports
		~~~~~~~ 
		[BaEx_SITC3_A] data='export', dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False
		[BaEx__SITC3_B] data='export', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False
		
		Imports
		~~~~~~~
		[BaIm_SITC3_A] data='import', dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False
		[BaIm_SITC3_B] data='import', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False

		Dynamic Consistent Datasets
		---------------------------
		Trade 
		~~~~~
		[DynTr_SITC3_C] data='trade', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False	
		[DynTr_SITC3_D] data='trade', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True

		Exports
		~~~~~~~
		[DynEx_SITC3_C] data='export', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False	
		[DynEx_SITC3_D] data='export', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True

		Imports 
		~~~~~~~
		[DynIm_SITC3_C] data='import', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False	
		[DynIm_SITC3_D] data='import', dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True

		Future Work
		===========
		[1] Construct a Dictionary of methods to dataset name
		"""
		raise NotImplementedError

	def construct_dataset_SC_CNTRY_SR2L3_Y62to00(self, data_type, dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False, report=True, source_institution='un', verbose=True):
		"""
		Construct a Self Contained (SC) Direct Action Dataset for Countries at the SITC Level 3
		Note: SC Reduce the Need to Debug many other routines for the time being. 
		The other methods are however useful to diagnose issues and to understand properties of the dataset

		STATUS: tests/test_constructor_SC_CNTRY_SR2L3_Y62to00.py

		data_type 				: 	'trade', 'export', 'import'

		Data Settings
		-------------
		dropAX 				: 	Drop AX Codes 
		sitcr2 				: 	Add SITCR2 Indicator
		drop_nonsitcr2 		: 	Drop non-standard SITC2 Codes
		intertemp_cntrycode : Generate Intertemporal Consistent Country Units (meta)
		drop_incp_cntrycode : Drop Incomplete Country Codes (meta)
		
		Other Settings
		--------------
		report 				: 	Print Report
		source_institution 	: which institutions SITC classification to use

		Operations:
		-----------
		[1] Drop SITC4 to SITC3 Level (for greater intertemporal consistency)
		[2] Import ISO3C Codes as Country Codes
		[3] Drop Errors in SITC3 codes ["" Codes]
			Optional:
			---------
			[A] Drop sitc3 codes that contain 'A' and 'X' codes [Default: True]
			[B] Drop Non-Standard SITC3 Codes [i.e. Aren't in the Classification]
			[C] Adjust iiso3c, eiso3c country codes to be intertemporally consistent
			[D] Drop countries with incomplete data across 1962 to 2000 (strict measure)

		Datasets
		--------
		[_A] dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False
		[_B] dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False
		[_C] dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False	
		[_D] dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True	

		Notes
		-----
		[1] This makes use of countryname_to_iso3c in the meta data subpackage
		[2] This method can be tested using /do/basic_sic3_country_data.do
		[3] DropAX + Drop NonStandard SITC Rev 2 Codes still contains ~94-96% of the data found in the raw data

		Future Work
		-----------
		[1] Check SITC Revision 2 Official Codes
		[2] Should this be split into a header function with specific trade, export, and import methods?
		[3] Add in Change Value Units to $'s (x 1000)
		"""
		from .meta import countryname_to_iso3c
		self.dataset_name = 'CNTRY_SR2L3_Y62to00_A'
		#-Checks-#
		if self.operations != "":
			raise ValueError("This Method requires a complete RAW dataset")
		if sum(self.years) != 77259: 																		#IS there a better way than this hack!
			raise ValueError("This Dataset must contain the full range of years to be constructed")
		#-Set Data-#
		df = self.dataset 
		df = df[['year', 'exporter', 'importer', 'sitc4', 'value']]
		#-SITC3-#
		df['sitc3'] = df.sitc4.apply(lambda x: x[0:3])
		df = df.groupby(['year', 'exporter', 'importer', 'sitc3']).sum()['value'].reset_index()
		self.level = 3
		#-Country Adjustment-#
		df = df.loc[(df.exporter != "World") & (df.importer != "World")]
		#-Exports (can include NES on importer side)-#
		if data_type == 'export' or data_type == 'exports':
			df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
			df = df.loc[(df.eiso3c != '.')]
			df = df.groupby(['year', 'eiso3c', 'sitc3']).sum()['value'].reset_index()
		#-Imports (can include NES on importer side)-#
		elif data_type == 'import' or data_type == 'imports':
			df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
			df = df.loc[(df.iiso3c != '.')]
			df = df.groupby(['year','iiso3c', 'sitc3']).sum()['value'].reset_index()
			#-Trade-#
		else: 
			df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
			df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
			df = df.loc[(df.iiso3c != '.') & (df.eiso3c != '.')]
			df = df.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum()['value'].reset_index()
		#-Product Code Errors in Dataset-#
		df = df.loc[(df.sitc3 != "")] 																	#Does this need a reset_index?
		#-dropAX-#
		if dropAX:
			if verbose: print "[INFO] Dropping SITC Codes with 'A' or 'X'"
			df['AX'] = df.sitc3.apply(lambda x: 1 if re.search("[AX]", x) else 0)
			df = df.loc[df.AX != 1]
			del df['AX']
		#-sitcr2-#
		if sitcr2:
			if verbose: print "[INFO] Adding SITCR2 Indicator"
			from pyeconlab.trade.classification import SITC
			sitc = SITC(revision=2, source_institution=source_institution)
			codes = sitc.get_codes(level=3)
			df['sitcr2'] = df['sitc3'].apply(lambda x: 1 if x in codes else 0)
			if drop_nonsitcr2:
				if verbose: print "[INFO] Dropping Non Standard SITCR2 Codes"
				df = df.loc[(df.sitcr2 == 1)]
				del df['sitcr2'] 				#No Longer Needed
		#-intertemp_cntrycode-#
		if intertemp_cntrycode:
			if verbose: print "[INFO] Imposing dynamically consistent iiso3c and eiso3c recodes across 1962-2000"
			from pyeconlab.util import concord_data
			from .meta import iso3c_recodes_for_1962_2000
			#-Export-#
			if data_type == 'export' or data_type == 'exports':
				df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['eiso3c'] != '.']
				df = df.groupby(['year', 'eiso3c', 'sitc3']).sum().reset_index()
			#-Import-#
			elif data_type == 'import' or data_type == 'imports':
				df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['iiso3c'] != '.']
				df = df.groupby(['year', 'iiso3c', 'sitc3']).sum().reset_index()
			#-Trade-#
			else:
				df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['iiso3c'] != '.']
				df = df[df['eiso3c'] != '.']
				df = df.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum().reset_index()
		#-drop_incp_cntrycode-#
		if drop_incp_cntrycode:
			if verbose: print "[INFO] Dropping countries with incomplete data across 1962-2000"
			from pyeconlab.util import concord_data
			from .meta import incomplete_iso3c_for_1962_2000
			#-Export-#
			if data_type == 'export' or data_type == 'exports':
				df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['eiso3c'] != '.']
			#-Import-#
			elif data_type == 'import' or data_type == 'imports':
				df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['iiso3c'] != '.']
			#-Trade-#
			else:
				df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False)) 	#issue_error = false returns x if no match
				df = df[df['iiso3c'] != '.']
				df = df[df['eiso3c'] != '.']
			df = df.reset_index()
			del df['index']
		#-Report-#
		if report:
			rdf = self.raw_data
			rdf = rdf.loc[(rdf.importer=="World") & (rdf.exporter == "World")]
			#-Year Values-#
			rdfy = rdf.groupby(['year']).sum()['value'].reset_index()
			dfy = df.groupby(['year']).sum()['value'].reset_index()
			y = rdfy.merge(dfy, how="outer", on=['year']).set_index(['year'])
			y['%'] = y['value_y'] / y['value_x'] * 100
			report = 	"Report construct_default_simple_sitc3(options)\n" + \
						"---------------------------------------\n"
			for year in self.years:
				report += "This dataset in year: %s captures %s percent of Total 'World' Values\n" % (year, int(y.ix[year]['%']))
			print report
		self._dataset = df

	def construct_dataset_SC_CNTRY_SR2L3_Y62to00_A(self, data_type, dataset_object=True, verbose=True):
		"""
		Complete Dataset Constructor for .construct_dataset_SC_CNTRY_SR2L3_Y62to00() [Dataset A]
		A => dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False

		data_type 	: 	'trade', 'export', 'import'
		dataset_object : True/False [Default: True]

		Note
		---- 
		[1] For Export/Import Data should use construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type='export'/'import') 
			as can aggregate with NES on the importer partner side which is dropped in the cleaned trade database

		"""
		self.construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type=data_type, dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False, report=verbose, verbose=verbose)
		if dataset_object:
			self.notes = "Computed with options dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False"
			obj = self.to_nberfeenstrawtf(data_type=data_type)
			return obj

	def construct_dataset_SC_CNTRY_SR2L3_Y62to00_B(self, data_type, dataset_object=True, verbose=True):
		"""
		Dataset Constructor for .construct_dataset_SC_CNTRY_SR2L3_Y62to00()	[Dataset B]
		B => dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False

		data_type 	: 	'trade', 'export', 'import'
		dataset_object : True/False [Default: True]

		Note
		---- 
		[1] For Export/Import Data should use construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type='export'/'import') 
			as can aggregate with NES on the importer partner side which is dropped in the cleaned trade database
		"""
		self.construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type=data_type, dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False, report=verbose, verbose=verbose)
		if dataset_object:
			self.notes = "Computed with options dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False"
			obj = self.to_nberfeenstrawtf(data_type=data_type)
			return obj

	def construct_dataset_SC_CNTRY_SR2L3_Y62to00_C(self, data_type, dataset_object=True, verbose=True):
		"""
		Dataset Constructor for .construct_dataset_SC_CNTRY_SR2L3_Y62to00() [Dataset C]
		C => dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False

		data_type 	: 	'trade', 'export', 'import'
		dataset_object : True/False [Default: True]

		Note
		---- 
		[1] For Export/Import Data should use construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type='export'/'import') 
			as can aggregate with NES on the importer partner side which is dropped in the cleaned trade database
		"""
		self.construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type=data_type, dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False, report=verbose, verbose=verbose)
		if dataset_object:
			self.notes = "Computed with options dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False"
			obj = self.to_nberfeenstrawtf(data_type=data_type)
			return obj

	def construct_dataset_SC_CNTRY_SR2L3_Y62to00_D(self, data_type, dataset_object=True, verbose=True):
		"""
		Dataset Constructor for .construct_dataset_SC_CNTRY_SR2L3_Y62to00() [Dataset D]
		C => dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True

		data_type 	: 	'trade', 'export', 'import'
		dataset_object : True/False [Default: True] 

		Note
		---- 
		[1] For Export/Import Data should use construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type='export'/'import') 
			as can aggregate with NES on the importer partner side which is dropped in the cleaned trade database
		"""
		self.construct_dataset_SC_CNTRY_SR2L3_Y62to00(data_type=data_type, dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True, report=verbose, verbose=verbose)
		if dataset_object:
			self.notes = "Computed with options dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True"
			obj = self.to_nberfeenstrawtf(data_type=data_type)
			return obj

	#-Dataset Construction Using Internal Methods-#

	def construct_dynamically_consistent_dataset(self, no_index=True, verbose=True):
		"""
		Constructs DEFAULT Dynamically Consistent Dataset for ProductCodes and CountryCodes
		Note: This can make debugging more difficult, and may wish to use an _SC_ dataset method (Self Contained)

		STATUS: **IN WORK**

		Operations
		----------
		Option A
		--------- 
		[1] Merge in Data at Raw Data Stage (China/HK Adjustments) & Delete sitc4 code issues
		[2] Collapse to Values Only (Keeping only ['year', 'icode', 'ecode', 'sitc4']) removes the Quantity Disaggregation
		[1] Alter Country Codes to be Intertemporally Consistent Units of Analysis (i.e. SUN = Soviet Union)
		[2] Collapse Values to SITCL3 Data
		[3] Remove Problematic Codes

		Future Work
		-----------
		[1] Work through these steps to ensure operations are on dataset and they flow from one to another
		[2] Write Tests for these methods as a priority
			[A] adjust_china_hongkongdata
			[B] collapse_to_valuesonly
		"""
		if self.complete_dataset != True:
			raise ValueError("Dataset must be a complete dataset!")	
		#--Merges at RAW DATA Phase--#
		self.delete_sitc4_issues_with_raw_data(verbose=verbose)
		self.load_china_hongkongdata(years=self.years, verbose=verbose) 									#Bring in China/HongKong Adjustments to supp_data
		self.adjust_china_hongkongdata(verbose=verbose)
		#-Reduction/Collapse-#
		self.collapse_to_valuesonly(subidx=['year', 'icode', 'ecode', 'sitc4'], verbose=verbose) 			#This will remove unit, quantity, dot, exporter and importer
		#--Collapse to SITCL3--#
		self.collapse_to_productcode_level(level=3, verbose=verbose) 		#Collapse to SITCL3 Level
		self.drop_alpha_productcodes(verbose=verbose) 						#Drop 1984 to 2000 alpha codes 
		#--Intertemporal CountryCode Adjustments--# 
		self.adjust_countrycodes_intertemporal(verbose=verbose)  	#Adds in iiso3c, eiso3c	etc
		#--Addition/Corrections to Dataset--#
		self.change_value_units(verbose=verbose) 							#Change Units to $'s
		self.add_sitcr2_official_marker(level=3, verbose=verbose) 			#Build SITCR2 Marker	
		self._dataset = self.dataset.set_index(keys=['year', 'eiso3c', 'iiso3c', 'sitc3'])
		if verbose:
			df = self.dataset
			print "Dataset Summary:"
			print "----------------"
			print "Number of Observations: %s" % df.shape[0]
			print "Number of Years: %s" % len(df.index.levels[0])
			print "Number of Exporters: %s" % len(df.index.levels[1])
			print "Number of Importers: %s" % len(df.index.levels[2])
			print "Number of Products: %s" % len(df.index.levels[3])
		if no_index:
			self._dataset = self.dataset.reset_index()
		return self.dataset


	#-----------------------------#
	#-PyEconLab Object Interfaces-#
	#-----------------------------#

	def attach_attributes_to_dataset(self):
		#-Attach Transfer Attributes-#
		self._dataset.txf_name 				= self._name
		self._dataset.txf_data_type 		= self.data_type
		self._dataset.txf_classification 	= self.classification
		self._dataset.txf_revision 			= self.revision 
		self._dataset.txf_complete_dataset 	= self.complete_dataset
		self._dataset.txf_notes 			= self.notes
		return self._dataset

	def to_nberfeenstrawtf(self, data_type, verbose=True):
		"""
		Construct NBERWTF Object with Common Core Object Names
		Note: This is constructed from the ._dataset attribute

		This will export the cleaned bilateral data to the NBERWTF object. 

		Arguments 
		---------
		data_type 	: 	'trade', 'export', 'import'

		Object Interface's
		------------------
		'trade' 	: 	['year', iiso3c', 'eiso3c', 'sitc[1-4]', 'value'] 	(Optional: 'quantity'?)
		'export' 	:	['year', 'eiso3c', 'sitc[1-4]', 'value']
		'import'	: 	['year', 'iiso3c', 'sitc[1-4]', 'value']

		Notes
		-----
		[1] It will be the responsibility of NBERWTF to export to ProductLevelExportSystems etc.

		Future Work 
		-----------
		[1] Add attribute to automatically determine what type of dataset is being exported 
		[2] Turn data_type into a self.data_type attribute!
		"""

		self.data_type = data_type

		sitcl = 'sitc%s' % self.level
		self._dataset = self.dataset.rename_axis({sitcl : 'productcode'}, axis=1)
		self.attach_attributes_to_dataset()

		if data_type == 'trade':
			return NBERWTFTrade(self.dataset)
		elif data_type == 'export' or data_type == 'exports':
			return NBERWTFExport(self.dataset)
		elif data_type == 'import' or data_type == 'imports':
			return NBERWTFImport(self.dataset)
		else:
			raise ValueError("data_type must be either 'trade', 'export(s)', or 'import(s)'")

	def to_dynamic_productleveltradesystem(self, verbose=True):
		"""
		Method to construct a ProductLevelTradeSystem from the dataset
		"""
		raise NotImplementedError

	def to_dynamic_productlevelexportsystem(self, verbose=True):
		"""
		Method to construct a Product Level Export System from the dataset
		Warning: This assumes the dataset contains the intended data
		Note: This requires 'export' data
		"""
		print "[WARNING] This method assumes the data in .dataset is the intended data"
		#-Prepare Names-#
		self._dataset.rename(columns={'eiso3c' : 'country', 'sitc3' : 'productcode', 'value' : 'export'}, inplace=True)
		self._dataset.set_index(['year'], inplace=True)
		#-Construct Object-#
		from pyeconlab.trade.systems import DynamicProductLevelExportSystem
		system = DynamicProductLevelExportSystem()
		system.from_df(df=self.dataset)
		return system

	def to_dynamic_productlevelimportsystem(self, verbose=True):
		"""
		Method to construct a Product Level Import System from the dataset
		Note: This requires 'import' data
		"""
		raise NotImplementedError
	

	# --------------------------------------------------------------- #
	# - META DATA FUNCTIONS 										- #
	# 																  #
	# - Note: These are largely for internal package construction   - #
	# - And for intertemporal diagnosis tables for sitc4 etc 	 	- #
	# --------------------------------------------------------------- #

	def generate_global_info(self, target_dir, out_type='py', verbose=False):
		"""
		Construct Global Information About the Dataset 
		
		Automatically import ALL data and Construct Unique:
		
		[1] Country List 	[Unique List of Countries in the Dataset]
		[2] Exporter List 	[Unique List of Exporters in the Dataset]
		[3] Importer List 	[Unique List of Exporters in the Dataset]
		[4] CountryName to ISO3C (REGEX) {py file only} [Requires Manual Adjustment]
		[5] CountryName to ISO3N (REGEX) {py file only}	[Requires Manual Adjustment]

		Note: 	The CountryName Concordances are automatically generated (currently using pycountrycode)
				These files should be checked for accuracy

		Parameters:
		-----------
			target_dir 	: 	target directory where files are to be written
							[Should specify REPO Location if updating REPO Files OR DATA_PATH if replace in Installed Package]
			out_type 	: 	file type for results files 'csv', 'py' 
							[Default: 'py']

		Usage:
		-----
		Useful if NBER Feenstra's Dataset get's updated etc. OR for constructing manual country concordances etc.

		Future Work:
		------------
		[1] Maybe this sort of information should be compiled by parsing the source files and importing only 
			the required information to save on time and memory! 
			(Update: Current Implementation of read.stata() doesn't allow selective import due to being a binary file)
		"""
		# - Check if Dataset is Complete for Global Info Property - #
		if self.complete_dataset != True:
			raise ValueError("Dataset must be complete. Try running the constructor without defining years=[]")
		# - Summary - #
		if verbose: 
			print "[INFO] Writing Exporter, Importer, and CountryLists to %s files in location: %s" % (out_type, target_dir)
		#-CSV-#
		if out_type == 'csv':
			# - Exporters - #
			pd.DataFrame(self.exporters, columns=['exporter']).to_csv(target_dir + 'exporters_list.csv', index=False)
			# - Importers - #
			pd.DataFrame(self.importers, columns=['importer']).to_csv(target_dir + 'importers_list.csv', index=False)
			# - Country List - #
			pd.DataFrame(self.country_list, columns=['country_list']).to_csv(target_dir + 'countryname_list.csv', index=False)
		#-PY-#
		elif out_type == 'py':
			# - Exporters - #
			s = pd.Series(self.exporters)
			s.name = 'exporters'
			from_series_to_pyfile(s, target_dir=target_dir, fl='exporters.py', docstring=self._name+': exporters'+'\n'+self.source_web)
			# - Importers - #
			s = pd.Series(self.importers)
			s.name = 'importers'
			from_series_to_pyfile(s, target_dir=target_dir, fl='importers.py', docstring=self._name+': importers'+'\n'+self.source_web)
			# - Country List - #
			s = pd.Series(self.country_list)
			s.name = 'countries'
			from_series_to_pyfile(s, target_dir=target_dir, fl='countrynames.py', docstring=self._name+': country list'+'\n'+self.source_web)
			# - CountryName to ISO3C, ISO3N Concordance - #
			self.countryname_concordance_using_cc(target_dir=target_dir, concord_vars=('countryname', 'iso3c'), verbose=verbose) 	#-This Obfuscates file construction and should probably return a dict with a matching from_dict_to_pyfile etc
			self.countryname_concordance_using_cc(target_dir=target_dir, concord_vars=('countryname', 'iso3n'), verbose=verbose)
		else:
			raise TypeError("out_type: Must be of type 'csv' or 'py'")
		
	def write_metadata(self, target_dir='./meta', verbose=True):
		"""
		Write Basic Files for ./meta in Excel Format for inclusion into the REPO

		Files
		-----
		[1] intertemporal_iiso3n.xlsx
		[2] intertemporal_eiso3n.xlsx
		[3] intertemporal_sitc4.xlsx

		Notes
		-----
		[1] Excel is currently used as an easy way to inspect the data
		[2] Not using local package location as mostly want to check output prior to entry through repo.
		"""
		#-Parse Directory-#
		target_dir = check_directory(target_dir)
		if verbose: print "Writing Meta Data Files to: %s" % target_dir
		#-Compute Intertemporal Tables of iiso3n and eiso3n-#
		table_iiso3n, table_eiso3n = self.intertemporal_countrycodes(verbose=verbose)
		table_iiso3n.to_excel(target_dir + 'intertemporal_iiso3n.xlsx')
		table_eiso3n.to_excel(target_dir + 'intertemporal_eiso3n.xlsx')
		#-Compute Intertemporal ProductCodes-#
		table_sitc4 = self.intertemporal_productcodes(verbose=verbose)
		table_sitc4.to_excel(target_dir + 'intertemporal_sitc4.xlsx')


	def intertemporal_tables(self, idx=['eiso3c'], value='value', force=False, verbose=False):
		"""
		Construct an Intertemporal Table (Wide Table of Data)
		
		force 		:  	True/False
						[Default: True => doesn't raise a ValueError if trying to conduct function on an incomplete dataset]

		Returns
		-------
			itable, etable
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Get Dataset-#
		df = self.dataset.copy(deep=True) 
		df = df[idx + ['year'] + [value]].groupby(idx +['year']).sum().unstack(level='year')
		return df

	# - Country Codes Meta - #

	def intertemporal_countrycodes(self, dataset=False, force=False, verbose=False):
		"""
		Wrapper for Generating intertemporal_countrycodes FROM 'raw_data' or 'dataset'
		"""
		if dataset:
			if verbose: print "Constructing Intertemporal Country Code Tables from Dataset ..."
			table_iiso3n, table_eiso3n = self.intertemporal_countrycodes_dataset(force=force, verbose=verbose)
			return table_iiso3n, table_eiso3n
		else:
			if verbose: print "Constructing Intertemporal Country Code Tables from RAW DATA ..."
			table_iiso3n, table_eiso3n = self.intertemporal_countrycodes_raw_data(force=force, verbose=verbose)
			return table_iiso3n, table_eiso3n

	def intertemporal_countrycodes_raw_data(self, force=False, verbose=False):
		"""
		Construct a table of importer and exporter country codes by year from RAW DATA
		Intertemporal Country Code Tables can also be computed from dataset using .intertemporal_countrycodes_dataset()
		which includes iso3c etc.

		force 		:  	True/False
						[Default: True => doesn't raise a ValueError if trying to conduct function on an incomplete dataset]

		Returns
		-------
			table_iiso3n, table_eiso3n
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Get Raw Data -#
		data = self.raw_data 		
		#-Split Codes-#
		if not check_operations(self, u"(split_countrycodes"): 							#Requires iiso3n, eiso3n
			if verbose: print "[INFO] Running .split_countrycodes() as is required ..."
			self.split_countrycodes(dataset=False, verbose=verbose)
		#-Core-#
		#-Importers-#
		table_iiso3n = data[['year', 'importer', 'icode', 'iiso3n']].drop_duplicates().set_index(['importer', 'icode', 'year'])
		table_iiso3n = table_iiso3n.unstack(level='year')
		table_iiso3n.columns = table_iiso3n.columns.droplevel() 	#Removes Unnecessary 'iiso3n' label
		#-Exporters-#
		table_eiso3n = data[['year', 'exporter', 'ecode', 'eiso3n']].drop_duplicates().set_index(['exporter', 'ecode', 'year'])
		table_eiso3n = table_eiso3n.unstack(level='year')
		table_eiso3n.columns = table_eiso3n.columns.droplevel() 	#Removes Unnecessary 'eiso3n' label
		return table_iiso3n, table_eiso3n

	def intertemporal_countrycodes_dataset(self, cid='default', force=False, verbose=False):
		"""
		Construct a table of importer and exporter country codes by year from DATASET
		This includes iso3c and is useful when using .countries_only() etc.
		
		force 		:  	True/False
						[Default: True => doesn't raise a ValueError if trying to conduct function on an incomplete dataset]

		Returns
		-------
			table_iiso3n, table_eiso3n
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Get Dataset-#
		data = self.dataset 
		#-Split Codes-#
		if 'eiso3n' not in data.columns or 'iiso3n' not in data.columns:
			if verbose: print "Running .split_countrycodes(force=True) as is required ..."
			self.split_countrycodes(iso3n_only=True, force=True, verbose=verbose)
		if not check_operations(self, u"add_iso3c"): 					
			if verbose: print "Running .add_iso3c() as is required ..."
			self.add_iso3c(verbose=verbose)
		#-Core-#
		cid_options = set(['importer', 'icode', 'iiso3n', 'iiso3c', 'exporter', 'ecode', 'eiso3n', 'eiso3c']) 	#Should this be a class attribute?
		if cid == 'default':
			cid = set(data.columns)
			cid = cid.intersection(cid_options)
		else:
			cid = set(cid)
			cid = cid.intersection(cid_options)
		if verbose: print "[INFO] Using country id code types: %s" % cid
		#-Compute icid, ecid-#
		icid, ecid = set(['iiso3n']), set(['eiso3n']) 			# Enforce ISO3N
		for item in cid: 
			if item[0] == 'i':
			 	icid.add(item)
			elif item[0] == 'e':
				ecid.add(item)
		#-Importers-#
		if verbose: print "[INFO] icid: %s" % list(icid)
		table_iiso3n = data[['year'] + list(icid)].drop_duplicates()
		icid.remove('iiso3n') 									 	#Fill Table with iiso3n data
		idx = list(icid) + ['year']
		table_iiso3n = table_iiso3n.set_index(idx)
		table_iiso3n = table_iiso3n.unstack(level='year')
		table_iiso3n.columns = table_iiso3n.columns.droplevel() 	#Removes Unnecessary 'iiso3n' label
		#-Exporters-#
		if verbose: print "[INFO] ecid: %s" % list(ecid)
		table_eiso3n = data[['year'] + list(ecid)].drop_duplicates()
		ecid.remove('eiso3n')
		idx = list(ecid) + ['year']
		table_eiso3n = table_eiso3n.set_index(idx)
		table_eiso3n = table_eiso3n.unstack(level='year')
		table_eiso3n.columns = table_eiso3n.columns.droplevel() 	#Removes Unnecessary 'eiso3n' label
		return table_iiso3n, table_eiso3n

	# - Product Codes Meta - #

	def intertemporal_productcodes_raw_data(self, force=False, verbose=False):
		"""
		Construct a table of productcodes by year
		
		force 		:  	True/False
						[Default: FALSE => raise a ValueError if trying to conduct function on an incomplete dataset]
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-RAW DATA-#
		data = self.raw_data 		
		#-Split Codes-#
		if not check_operations(self, u"(split_countrycodes)"): 						#Requires iiso3n, eiso3n
			if verbose: print "Running .split_countrycodes() as is required ..."
			self.split_countrycodes(dataset=False, verbose=verbose)
		#-Core-#
		table_sitc4 = data[['year', 'sitc4']].drop_duplicates()
		table_sitc4['code'] = 1
		table_sitc4 = table_sitc4.set_index(['sitc4', 'year']).unstack(level='year')
		#-Drop TopLevel Name in Columns MultiIndex-#
		table_sitc4.columns = table_sitc4.columns.droplevel() 	#Removes Unnecessary 'code' label
		return table_sitc4

	def intertemporal_productcodes_dataset(self, tabletype='indicator', meta=True, countries='None', cpidx=True, source_institution='un', level=-1, force=False, verbose=False):
		"""
		Construct a table of productcodes by year
		This is different to the RAW DATA method as it adds in meta data such as SITC ALPHA MARKERS AND Official SITCR2 Indicator
		
		tabletype 	: 	['indicator', 'value', 'composition']
		meta 		: 	True/False
						Adds SITCR2 Marker in the Index
		countries 	: 	['None', 'exporter', 'importer']
						Default = 'None'
		level 		: 	Level for Composition Table
		force 		:  	True/False
						[Default: FALSE => raise a ValueError if trying to conduct function on an incomplete dataset]
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Core-#
		if tabletype == 'value':
			return self.intertemporal_productcodes_dataset_values(meta=meta, countries=countries, cpidx=cpidx, source_institution=source_institution, \
																	force=force, verbose=verbose)
		elif tabletype == 'composition':
			return self.intertemporal_productcodes_dataset_compositions(meta=meta, countries=countries, cpidx=cpidx, source_institution=source_institution, \
																	level=level, force=force, verbose=verbose)
		else: 																																		# 'indicator' if not other match found
			return self.intertemporal_productcodes_dataset_indicator(meta=meta, countries=countries, cpidx=cpidx, source_institution=source_institution, \
																	force=force, verbose=verbose)				
	

	def intertemporal_productcodes_dataset_indicator(self, meta=True, countries='None', cpidx=True, source_institution='un', force=False, verbose=False):
		"""
		Construct a table of productcodes by year
		This is different to the RAW DATA method as it adds in meta data such as SITC ALPHA MARKERS AND Official SITCR2 Indicator
		
		meta 		: 	True/False
						Adds SITCR2 Marker in the Index
		force 		:  	True/False
						[Default: FALSE => raise a ValueError if trying to conduct function on an incomplete dataset]
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		sitcl = "sitc%s" % self.level
		#-DATASET-#
		data = self.dataset
		#-ParseCountries-#
		if countries == 'exporter':
			idx = ['year', 'exporter', sitcl]
		elif countries == 'importer':
			idx = ['year', 'importer', sitcl]
		else:
			idx = ['year', sitcl]
		#-Core-#													
		table_sitc = data[idx].drop_duplicates()
		table_sitc['attr'] = 1 																							
		table_sitc = table_sitc.set_index(idx).unstack(level='year')
		table_sitc.columns = table_sitc.columns.droplevel()  								#Drop TopLevel Name 'attr' in Columns MultiIndex
		#-Add Coverage Stats-# 																#Note this isn't classified as meta
		total_coverage = len(table_sitc.columns)
		table_sitc['Coverage'] = table_sitc.sum(axis=1)
		table_sitc['%Coverage'] = table_sitc['Coverage'] / total_coverage				
		#-Add in Meta for ProductCodes-#
		if meta:
			#-SITCR2-#
			pidx = table_sitc.index.names
			table_sitc = table_sitc.reset_index()
			sitc = SITC(revision=2, source_institution=source_institution)
			codes = sitc.get_codes(level=self.level)
			table_sitc['SITCR2'] = table_sitc[sitcl].apply(lambda x: 1 if x in codes else 0)
			table_sitc = table_sitc.set_index(pidx + ['SITCR2'])
		if not cpidx and countries in ['exporter', 'importer']:
			if meta:
				table_sitc = table_sitc.reorder_levels([1,0,2]).sort_index() 								#Swap Country and Product
			else:
				table_sitc = table_sitc.reorder_levels([1,0]).sort_index() 
		return table_sitc

	def intertemporal_productcodes_dataset_values(self, meta=True, countries='None', cpidx=True, source_institution='un', force=False, verbose=False):
		"""
		Construct a table of productcodes by year containing Values
		This is different to the RAW DATA method as it adds in meta data such as SITC ALPHA MARKERS AND Official SITCR2 Indicator
		
		meta 		: 	True/False
						Adds SITCR2 Marker in the Index
		force 		:  	True/False
						[Default: FALSE => raise a ValueError if trying to conduct function on an incomplete dataset]
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		sitcl = 'sitc%s' % self.level
		#-DATASET-#
		data = self.dataset 
		#-ParseCountries-#
		if countries == 'exporter':
			idx = ['year', sitcl, 'exporter', 'value']
			gidx = ['exporter', sitcl, 'year']
		elif countries == 'importer':
			idx = ['year', sitcl, 'importer', 'value']
			gidx = ['importer', sitcl, 'year']
		else:
			idx = ['year', sitcl, 'value']
			gidx = [sitcl, 'year']
		#-Core-#
		table_sitc = data[idx].groupby(gidx).sum()
		table_sitc = table_sitc.unstack(level='year') 	
		table_sitc.columns = table_sitc.columns.droplevel() 								#Drop 'value' Name in Columns MultiIndex
		#-Add in Meta for ProductCodes-#
		if meta:
			#-RowTotals-#
			yearcols = []
			for year in self.years:
				yearcols.append(year)
			table_sitc['Tot'] = table_sitc[yearcols].sum(axis=1)
			table_sitc['Avg'] = table_sitc[yearcols].mean(axis=1)
			table_sitc['Min'] = table_sitc[yearcols].min(axis=1)
			table_sitc['Max'] = table_sitc[yearcols].max(axis=1)
			#-Coverage Stats-#
			coverage = self.intertemporal_productcodes_dataset_indicator(meta=False, countries=countries, cpidx=cpidx, force=force)[['Coverage', '%Coverage']]
			table_sitc = table_sitc.merge(coverage, left_index=True, right_index=True)
			#-SITCR2-#
			pidx = table_sitc.index.names
			table_sitc = table_sitc.reset_index()
			sitc = SITC(revision=2, source_institution=source_institution)
			codes = sitc.get_codes(level=self.level)
			table_sitc['SITCR2'] = table_sitc[sitcl].apply(lambda x: 1 if x in codes else 0)
			table_sitc = table_sitc.set_index(pidx + ['SITCR2'])
		if not cpidx and countries in ['exporter', 'importer']:
			if meta:
				table_sitc = table_sitc.reorder_levels([1,0,2]).sort_index()  								#Swap Country and Product
			else:
				table_sitc = table_sitc.reorder_levels([1,0]).sort_index() 
		return table_sitc

	def intertemporal_productcodes_dataset_compositions(self, meta=True, countries='None', cpidx=True, source_institution='un', level=-1, force=False, verbose=False):
		"""
		Construct a table of productcodes by year
		This is different to the RAW DATA method as it adds in meta data such as SITC ALPHA MARKERS AND Official SITCR2 Indicator
		
		meta 		: 	True/False
						Adds SITCR2 Marker in the Index
		level 		: 	Level for Composition Table
						Default: 1 x Level Higher than Data in the Dataset (i.e. 4 would generate compositions with level 3 codes)
		force 		:  	True/False
						[Default: FALSE => raise a ValueError if trying to conduct function on an incomplete dataset]

		Issue
		-----
		[1] np.nan is being teated as 100% in composition Tables
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Aggregation Level Option-#
		if level == -1:
			level = self.level - 1
		sitcl = 'sitc%s' % self.level
		#-DATASET-#
		data = self.dataset 
		#-ParseCountries-#
		if countries == 'exporter':
			idx = ['year', sitcl, 'exporter', 'value']
			gidx = ['exporter', sitcl, 'year']
		elif countries == 'importer':
			idx = ['year', sitcl, 'importer', 'value']
			gidx = ['importer', sitcl, 'year']
		else:
			idx = ['year', sitcl, 'value']
			gidx = [sitcl, 'year']
		#-Core-#
		table_sitc = self.intertemporal_productcode_valuecompositions(level=level, countries=countries) 		
		#-Add in Meta for ProductCodes-#
		if meta:
			#-Mean/Min/Max-#
			yearcols = []
			for year in self.years:
				yearcols.append(year)
			table_sitc['Avg'] = table_sitc[yearcols].mean(axis=1)
			table_sitc['Min'] = table_sitc[yearcols].min(axis=1)
			table_sitc['Max'] = table_sitc[yearcols].max(axis=1)
			table_sitc['AvgNorm'] = table_sitc[yearcols].sum(axis=1).div(len(self.years)) 		#Normalised by Number of Years (Average Composition over Time) np.nan = 0
			#-Coverage-#
			coverage = self.intertemporal_productcodes_dataset_indicator(meta=False, countries=countries, cpidx=True, force=force)[['Coverage', '%Coverage']] 	#need cpindex to merge
			table_sitc = table_sitc.merge(coverage, left_index=True, right_index=True)
			#-SITCR2-#
			pidx = table_sitc.index.names
			table_sitc = table_sitc.reset_index()
			sitc = SITC(revision=2, source_institution=source_institution)
			codes = sitc.get_codes(level=self.level)
			table_sitc['SITCR2'] = table_sitc[sitcl].apply(lambda x: 1 if x in codes else 0)
			table_sitc = table_sitc.set_index(pidx+['SITCR2'])
		if not cpidx and countries in ['exporter', 'importer']:
			if meta:
				table_sitc = table_sitc.reorder_levels([1,0,2]).sort_index()  								#Swap Country and Product
			else:
				table_sitc = table_sitc.reorder_levels([1,0]).sort_index() 
		return table_sitc

	def intertemporal_productcode_valuecompositions(self, level=-1, countries='None', verbose=False):
		"""
		Produce Value Composition Tables for Looking at SITC4 relative to some other level of aggregation

		level 	: 	Aggregation Level to compute compositions for.
		countries : 	Allow for Tables to be generated for exporter, level or importer, level or just level 

		Note
		----
		[1] Write Tests
		[2] This could be a dataframe.py utility
		"""
		#-DATASET-#
		data = self.dataset
		#-Aggregation Level Option-#
		if level == -1:
			level = self.level - 1
		sitcld = 'sitc%s'% self.level
		sitcl = 'sitc%s' % level
		#-ParseCountries-#
		if countries == 'exporter':
			idx = ['year', sitcld, 'exporter', 'value'] 			#base
			gidx = ['exporter', sitcld, 'year'] 					#groupby base idx
			lidx = ['year', sitcl, 'exporter', 'value']				#level idx
			glidx = ['year', sitcl, 'exporter'] 					#groupby level idx
			midx = ['year', sitcld, sitcl.upper(), 'exporter'] 		#merge idx
			msidx = ['year', 'exporter', sitcld]
		elif countries == 'importer':
			idx = ['year', sitcld, 'importer', 'value']
			gidx = ['importer', sitcld, 'year']
			lidx = ['year', sitcl, 'importer', 'value']
			glidx = ['year', sitcl, 'importer']
			midx = ['year', sitcld, sitcl.upper(), 'importer']
			msidx = ['year', 'importer', sitcld]
		else:
			idx = ['year', sitcld, 'value']
			gidx = [sitcld, 'year']
			lidx = ['year', sitcl, 'value']
			glidx = ['year', sitcl]
			midx = ['year', sitcld, sitcl.upper()]
			msidx = ['year', sitcld]
		#-Core-#
		#-SITC4-#
		table_sitc = data[idx].groupby(gidx).sum().reset_index()
		table_sitc[sitcl] = table_sitc[sitcld].apply(lambda x: str(x)[:level])
		#-SITCL-#
		table_sitcl = data[idx].groupby(gidx).sum().reset_index()
		table_sitcl[sitcl] = table_sitcl[sitcld].apply(lambda x: str(x)[:level])
		table_sitcl = table_sitcl[lidx].groupby(glidx).sum().reset_index()
		#-Construct Table-#
		table = table_sitc.merge(table_sitcl, on=glidx)
		table[sitcl.upper()] = table['value_x'] / table['value_y'] * 100
		table = table[midx]
		table = table.set_index(msidx)
		table = table.unstack(level='year')
		table.columns = table.columns.droplevel()
		return table 

	def intertemporal_productcode_countries(self, meta=True, force=False, verbose=False):
		"""
		Compute Number of Country Exporters for Any Given ProductCode
		"""
		df = self.intertemporal_productcodes_dataset_indicator(meta=meta, countries='exporter')
		df = df.reset_index()
		sitcl = 'sitc%s' % self.level
		if meta:
			df = df.groupby([sitcl, 'SITCR2']).sum()
			#-Higher Aggregation of Coverage Stats-#
			df = df.drop(['Coverage', '%Coverage'], axis=1)
			coverage = self.intertemporal_productcodes_dataset_indicator(meta=False, force=force)[['Coverage', '%Coverage']]
			df = df.merge(coverage, left_index=True, right_index=True)
		else:
			df = df.groupby([sitcl]).sum()
		return df

	def intertemporal_productcode_adjustments_table(self, force=False, verbose=False):
		"""
		[STATUS: EXPERIMENTAL] Documents and Produces the Adjustments Table for Meta Data Reference 
		
		force 	: 	True/False - Check if Complete Dataset 
					[Default: False]

		Looking at SITCL3 GROUPS
		------------------------
		[1] For each Unofficial 'sitc4' Code Ending with '0' check if Official Codes in the SAME LEAF are CONTINUOUS. IF they ARE keep the CHILDREN as they are 
			disaggregated classified goods ELSE wrap up the data into the Unofficial '0' Code as these groups have intertemporal classification issues for the 1962-2000
			dataset

			[a] is dropping the '0' unofficial category systemically dropping certain countries data from the dataset?** See [2] in Notes
			[b] What is the value of unofficial codes categories by year?

		Looking at 'A' and 'X' Groups
		-----------------------------
		[1] Remove 'A' and 'X' Codes as they are assignable and hold relatively little data (these will be captured in SITCL3 Dataset as a robustness check)
		 	Supporting Evidence can be considered with .compute_valAX_sitclevel() method

		Method
		------
		[1] Collapse A and X Codes into the Unofficial Code Line (IF AVAILABLE)
			IF NOT AVAILABE: DELETE
		[2] Check EACH SITCL3 GROUP and compare the Unofficial Code '0' with the Official Codes within the group. 
			IF Children == FULL COVERAGE (i.e. 39) then keep Children AND DELETE UNOFFICIAL Line
			IF Children != FULL COVERAGE (i.e 30) then collapse sum the Children into the Unoficial line item

		Notes
		-----
		[1] '025*'' and '011*'' are good examples and test cases	
		[2] Check meta/xlsx/intertemporal_sitc4_compositions_wmeta_adjustments.xlsx to review and check output
			{A} We should check how many countries are using the unofficial code vs. the official codes in each group as this may effect intercountry 
				variation. By deleting the Unofficial Level 3 Code this may be systemically removing exports from some developing countries. A full
				treatment of countries needs to be done for each SITCL3 subgroup to decide the best collapse and deletion strategy.
				Case Study: '057*' => Check Exporters using '0570' and exporters using '0571' to '0577'
		[3] This table suggests that SITCL3 should be used for inter-temporal consistency re: 2-A remark.  
		"""
		#-Core-#
		comp = self.intertemporal_productcodes_dataset(tabletype='composition', meta=True, level=3, force=force)
		idxnames = comp.index.names
		colnames = comp.columns
		comp = comp.reset_index()
		comp['SITCL3'] = comp['sitc4'].apply(lambda x: str(x)[:3])
		comp['4D'] = comp['sitc4'].apply(lambda x: str(x)[3:])       	 
		# comp = comp.loc[(comp.SITCL3 == '011') | (comp.SITCL3 == '025')] 	#Test Filter. Think about special cases when remove
		r = pd.DataFrame()
		for idx, df in comp.groupby(by=['SITCL3']):
			s1 = df[['SITCR2', '%Coverage']].groupby(by=['SITCR2']).mean()['%Coverage'] #Average Coverage Within SITCL3
			try: 
				avg_official_coverage = s1[1]
			except: 
				avg_official_coverage = 0
			try:
				avg_notofficial_coverage = s1[0]
			except:
				avg_notofficial_coverage = 0
			s2 = df[['SITCR2', 'Avg']].groupby(by=['SITCR2']).sum()['Avg']
			try:
				comp_official = s2[1]
			except:
				comp_official = 0
			try:
				comp_notofficial = s2[0]
			except: 
				comp_notofficial = 0
			if avg_official_coverage > 0.95 and comp_official >0.95:
			    df['ACTION'] = df['SITCR2'].apply(lambda x: 'K' if x == 1 else 'D')              #Keep Offical Codes, Delete Unofficial
			else:
			    df['ACTION'] = 'C' # Collapse ALL Codes
			r = r.append(df[list(idxnames)+list(colnames)+['ACTION']])
		r = r.set_index(list(idxnames))
		return r


	def compute_cases_intertemporal_sitc4_3digits(self, force=False, verbose=False):
		"""
		[STATUS: EXPERIMENTAL] Compute a Cases Table for SITC4 Intertemporal ProductCodes at the 3 Digit Level

		STATUS: IN-WORK

		Cases
		-----
		For Each SITC Level 3 Group apply a classifier for the following cases

		'Case1' 	: 	Avg(Official Coverage) 					> 95% (Official Codes are represented across 95% of the years on average)
						Avg(Composition % of Official Codes) 	> 95% (most of the value lies in Official encodings across al 39 years)
						{This shows groups that are represented by a majority of trade flows in official SITCR2 Codes across the whole dataset i.e. 0011)

		'Case2' 	: 	Unofficial Code Ending in '0' is present
						{This will highlight groups that have an Unofficial 3Digit Level Code Present in the data. 
						These groups suffer heavily from inter-country heterogeneity in how similar products are grouped} 

		'Case3' 	: 	??

		"""
		
		#-Core-#
		comp = self.intertemporal_productcodes_dataset(tabletype='composition', meta=True, level=3, force=force)
		idxnames = comp.index.names
		colnames = comp.columns
		comp = comp.reset_index()
		comp['SITCL3'] = comp['sitc4'].apply(lambda x: str(x)[:3])
		comp['4D'] = comp['sitc4'].apply(lambda x: str(x)[3:])       	 
		# comp = comp.loc[(comp.SITCL3 == '011') | (comp.SITCL3 == '025')] 	#Test Filter. Think about special cases when remove
		r = pd.DataFrame()
		for idx, df in comp.groupby(by=['SITCL3']):
			#-Case1-#
			s1 = df[['SITCR2', '%Coverage']].groupby(by=['SITCR2']).mean()['%Coverage'] #Average Coverage Within SITCL3
			try: avg_official_coverage = s1[1]
			except: avg_official_coverage = 0
			s2 = df[['SITCR2', 'Avg']].groupby(by=['SITCR2']).sum()['Avg']
			try: comp_official = s2[1]
			except: comp_official = 0
			if avg_official_coverage > 0.95 and comp_official >0.95:
			    df['CASE1'] = 1
			else:
			    df['CASE1'] = 0
			#-Case2-#
			if len(df.loc[(df.sitc4 == str(idx)+'0') & (df.SITCR2 == 0)]) == 1:
				df['CASE2'] = 1
			else:
				df['CASE2'] = 0
			r = r.append(df[list(idxnames)+list(colnames)+['CASE1', 'CASE2']])
		r = r.set_index(list(idxnames))
		return r


	# -------------- #
	# - Converters - #
	# -------------- #

	def convert_stata_to_hdf_yearindex(self, format='table', verbose=True):
		"""
		Convert the Raw Stata Source Files to a HDF File Container indexed by Y#### (where #### = year)

		Future Work
		-----------
		[1] Integrity Checking against original dta file hash?
		[2] Move this to a Utility?
		[3] Is there a way to make this work across 4 cores writing separate container names? 
			May require separate h5 files
		"""
		#Note: This might write into a dataset!
		years = self._available_years
		hdf_fn = self._source_dir + self._fn_prefix + str(years[0])[-2:] + '-' + str(years[-1])[-2:] + '_yearindex' + '.h5' 	
		pd.set_option('io.hdf.default_format', format)
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		self.__raw_data_hdf_yearindex = hdf 									#SHould this be a filename rather than a Container?

		#-Convert Files -#					
		for year in self._available_years:
			dta_fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Converting file: %s to file: %s" % (dta_fn, hdf_fn)
			#pd.read_stata(dta_fn).to_hdf(hdf_fn, 'Y'+str(year))
			hdf.put('Y'+str(year), pd.read_stata(dta_fn), format=format)
			
		print hdf
		hdf.close()


	def convert_raw_data_to_hdf(self, format='table', verbose=True):
		"""
		Convert the Entire RAW Data Compilation to a HDF File with index 'raw_data'

		complevel : compression level

		Future Work
		-----------
		[1] Integrity Checking against original dta file hash?
		[2] Move this to a Utility?
		"""
		years = self._available_years
		hdf_fn = self._source_dir + self._fn_prefix + str(years[0])[-2:] + '-' + str(years[-1])[-2:] +  '_raw' + '.h5'
			# hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
			# self.__raw_data_hdf = hdf
			# pd.set_option('io.hdf.default_format', 'table')
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		hdf.put('raw_data', self.__raw_data, format=format)
		if verbose: print hdf
		hdf.close()


	# - Issues with Raw Data - #
	# ------------------------ #

	def issues_with_raw_data(self):
		"""
		Documents observed issues with the RAW DATA
		Note: This products files from where it is called

		[1] Missing SITC4 Codes (28 observations) -> './missing_sitc4.xlsx'
		"""
		#-Missing Codes-#
		codelength = self.raw_data['sitc4'].apply(lambda x: len(x))
		self.raw_data[codelength != 4].to_excel('missing_sitc4.xlsx')


	# ----------------------- #
	# - Construct Test Data - #
	# ----------------------- #

	def testdata_collapse_to_valuesonly(self, size=10):
		"""
		Produce Test Data to check method: collapse_to_valuesonly

		size 	: sample size of 10 different duplicate scenarios
		
		Returns 
		-------
		Tuple(data, result)
			data 	: 	which contains all instances of the random sample 
			result 	:	which contains the collapse_to_valuesonly result	

		Notes
		-----
		[1] Sample Data can be saved to csv or xlsx and aggregated to check against result
		"""	
		idx = ['year', 'icode',	'importer',	'ecode', 'exporter', 'sitc4']
		#-Find Duplicate Lines by IDX-#
		dup = self.raw_data.duplicated(subset=idx) 										
		#-Generate a Random Sample-#
		sample = random_sample(self.raw_data[dup], size)
		sample = sample.reset_index()
		
		#-Find All Rows Contained in the Sample from the Dataset to check Collapse-#
		data = pd.DataFrame()
		for i, row in sample[idx].iterrows():
			data = data.append(find_row(self.raw_data[idx], row))
		#-Full Table of Results-#
		data = self.raw_data.ix[data.index]
		
		#-Compute Result-#
		self.collapse_to_valuesonly() 										#Note: This actually runs the collapse and produces self.dataset
		result = pd.DataFrame()
		for i, row in sample[idx].iterrows():
			result = result.append(find_row(self.dataset[idx], row))
		result = self.dataset.ix[result.index]

		return data, result

	def testdata_construct_dynamically_consistent_dataset(self, size=20):
		"""
		Product Tests Data to check: construct_dynamically_consistent_dataset
		"""
		raise NotImplementedError


	#--------------#
	#-Case Studies-#
	#--------------#

	def case_study_useofsitc3_exporterhetero_code(self, code):
		"""
		Composition Study on SITC Code [ie. code='057']

		Purpose
		-------
		This study products a table of 'exporter' compositional data. The Composition is the percent 
		of exports from that country attributed to each SITC4 digit code for a level 3 code such as '057'. 
		This table shows  significant cross-country heterogeneity in how countries "use" the coding system. 

		In the 1960's data for Australia coded '0570' makes up ~36% of the category. If a dataset is 
		constructed using only official codes then 36% of Australia's export in this family of products 
		would be dropped from the sample from the 1960's. 
		However in the case of Brazil, this line item '0570' is not used much at all (~0.3%) and it's exports 
		would be relatively unchanged. 

		Note: Cross Sections can still be studied with the high level of disaggregation. But for dynamic studies,
		these compositional affects will skew export lines showing export growth and decline in cases of compositional 
		shift from one to another coding system.

		Main Outcome
		------------
		[1] For dynamic consistency between 1962 and 2000 the only real option is to aggregate families of goods to the 3-Digit Level
			This aggregation will also capture A and X adjustments and countries usuing the high level classification with records 
			found in '0' categories that aren't always found in the SITCR2 classification. 
		[2] For dynamic consistency from 1984 onwards, it is possible to use SITCR2 official codes. 

		"""
		self.countries_only()
		df = self.intertemporal_productcodes_dataset(tabletype='composition', countries='exporter')
		df = df.reset_index()
		df['sitc3'] = df['sitc4'].apply(lambda x: str(x)[:3])
		df = df.set_index(['sitc3', 'exporter', 'sitc4'])
		df = df.ix[str(code)[0:3]]
		df.name = code
		return df












	# --------------------------------------- #
	# - Below is Temporary Work (Ideas etc) - #
	# --------------------------------------- #

	def compute_importer_value_percentofdataset(self):
		""" 
		Simple Compute of Importer Share in RAW DATA Dataset
		
		Note
		----
		[1] These are not trade shares
		"""
		total = self.raw_data['value'].sum() 			#Note this includes WLD etc
		perc = self.raw_data.groupby(['importer'])['value'].sum() / total * 100
		return perc

	def compute_exporter_value_percentofdataset(self):
		""" 
		Simple Compute of Importer Share in RAW DATA Dataset
		
		Note
		----
		[1] These are not trade shares
		"""
		total = self.raw_data['value'].sum() 			#Note this includes WLD etc
		perc = self.raw_data.groupby(['exporter'])['value'].sum() / total * 100
		return perc

	def return_nes_items(self, column):
		""" 
		Returns Note Elsewhere Specified (NES) Items through matching on a Regular Expression

		column 	: 	'importer' or 'exporter'

		"""
		return self.raw_data[self.raw_data[column].isin(set([x for x in a.raw_data[column] if re.search(r'\bnes', x.lower())]))]


	def build_countrynameconcord_add_iso3ciso3n(self, force=False, verbose=False):
		""" 
		Builds a CountryName Concordance and adds in iso3c and iso3n codes to dataset
		
		STATUS: DEPRECATED
		
		Notes
		-----
		[1] Better to Match on ISO3N through countrycodes component
		"""
		#-Build Country Name Concordance-#
		if verbose: print "[INFO] Building Country Name Concordance and adding iso3c and iso3n names"
		concord = self.countryname_concordance_using_cc(return_concord=True, force=force)
		#-Add ISO3C and ISO3N Data-#
		#-Importers-#
		self._dataset = self._dataset.merge(concord, left_on=['importer'], right_on=['countryname'])
		del self._dataset['countryname']
		self._dataset = self._dataset.rename_axis({'iso3c' : 'iiso3c', 'iso3n' : 'iiso3n'}, axis=1)
		#-Exporters-#
		self._dataset = self._dataset.merge(concord, left_on=['exporter'], right_on=['countryname'])
		del self._dataset['countryname']
		self._dataset = self._dataset.rename_axis({'iso3c' : 'eiso3c', 'iso3n' : 'eiso3n'}, axis=1)

	def load_data(years=[], keep_columns='all', verbose=None):
		"""
		Load Data

		years 			: specify years
		keep_columns 	: specify columns in the dataset to keep

		Notes:
		------
		[1] read_stata in pandas doesn't allow for importing columns
		[2] May want to re-write the __init__ portion to fetch data using this method
		[3] This still imports a LOT of necessary data!
		"""
		data = pd.DataFrame()
		if years == []:
			years = self._available_years
		for year in years:
			fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Fetching 'countryname' Year: %s from file: %s" % (year, fn)
			if keep_columns != 'all':
				data = data.append(pd.read_stata(fn)[keep_columns])
			else:
				data = data.append(pd.read_stata(fn))
		return data

	def generate_countryname_concordance_files(self, verbose=False):
		"""
		Generate a Global CountryName Concordance File for NBERWTF Dataset

		STATUS: **ON HOLD** 
				(Given this saves no time (and memory isn't binding) this function is currently ON HOLD)
				Feature Request made to pydata/pandas #7935

		Tasks
		-----
		[1] Load CountryName Only from dta files (Make a self.load_data(keep_columns=None) where keep_columns=['countryname'] in this method?)
		[2] Have to read all the data in pandas.read_stata() but much more memory efficient to discard the rest of the results for updating package files etc.
		[2] Write Concordance using pycountrycode to package data folder

		Output (DATA_PATH)
		------------------
		nberfeenstrawtf(countryname)_to_iso3c.py, nberfeenstrawtf(countryname)_to_iso3n.py, 

		Notes:
		------
		[1] Add to docstring "manually checked: False" as the results are determined by a regular expression
			Early Versions should be checked
		[2] The only advantage to this method is memory efficiency. It isn't any quicker. 
		"""

		countrynames = set()
		
		#-Load 'countrynames' from ALL Available Years-#
		for year in self._available_years:
			fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Fetching 'countryname' Year: %s from file: %s" % (year, fn)
			data = pd.read_stata(fn)[['importer', 'exporter']] 									#Note: This still reads in ALL of the .dta file! Feature Request made to pydata/pandas #7935
			importers = set(data['importer'])
			exporters = set(data['exporter'])
			countrynames = countrynames.union(importers).union(exporters)
			del data
		
		#- Concordance -#
		if verbose: print "Writing CountryName to ISO3C and ISO3N Files to %s" % DATA_PATH
		
		#-ISO3C-#
		iso3c = countryname_concordance(list(countrynames), concord_vars=('countryname', 'iso3c'))
		#-Write Py File-#
		iso3c.name = u"%s to %s" % ('countryname', 'iso3c')
		fl = "%s_%s_%s.py" % (self._name, 'countryname', 'iso3c')
		docstring 	= 	u"Concordance for %s to %s\n\n" % ('countryname', 'iso3c') 	+ \
						u"%s" % self
		from_idxseries_to_pydict(iso3c, target_dir=DATA_PATH, fl=fl, docstring=docstring)
		
		#-ISO3C-#
		iso3n =  countryname_concordance(list(countrynames), concord_vars=('countryname', 'iso3n'))
		#-Write Py File-#
		iso3n.name = u"%s to %s" % ('countryname', 'iso3n')
		fl = "%s_(%s)_%s.py" % (self._name, 'countryname', 'iso3n')
		docstring 	= 	u"Concordance for %s to %s\n\n" % ('countryname', 'iso3n') 	+ \
						u"%s" % self
		from_idxseries_to_pydict(iso3n, target_dir=DATA_PATH, fl=fl, docstring=docstring)


	def file_raw_data_to_hdf(self, verbose=True):
		"""
		Move self.raw_data attribute to reference a h5 file on disk (to free up memory)
		
		Notes
		-----
		[1] Move to Generic Class of DatasetConstructors?
		[2] This isn't particularly Useful in this context, as attributes are derived from raw_data and it will 
			be automatically reloaded to memory. 
		"""
		try:
			fn = self._source_dir + self.__raw_data_hdf_fn
			if verbose: print "[INFO] Attaching HDFStore to: %s" % fn
			self.__raw_data_hdf = pd.HDFStore(fn) 							#Check if file already exists
		except:
			if verbose: print "[INFO] raw data h5 file not found! Constructing one ..."
			self.convert_raw_data_to_hdf(verbose=verbose)  				#self.__raw_data_hdf = hdf	
		if verbose: print 	"[INFO] Deleting in-memory raw_data\n" 									 + \
							"You can still access raw_data but it will need to be loaded into memory"
		del self.__raw_data