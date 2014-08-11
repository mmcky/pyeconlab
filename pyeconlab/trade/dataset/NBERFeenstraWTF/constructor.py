# -*- coding: utf-8 -*-
"""
NBERFeenstraWTF Constructer

Compile NBERFeenstra RAW data Files and Perform Basic Data Preparation Tasks

Conventions
-----------
__raw_data 	: Should be an exact copy of the imported files and protected. 
dataset 	: Contains the Modified Dataset

Notes
-----
A) Load Times
[1] a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='hdf') [~41s] 		From a complevel=9 file (Filesize: 148Mb)
[2] a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='hdf') [~34.5s]   	From a complevel=0 file (FileSize: 2.9Gb)
[3] a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='dta') [~14min 23s]

B) Convert Times (from a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR, ftype='dta'))
[1] a.convert_raw_data_to_hdf(complevel=0) [1min 21seconds]
[2] a.convert_raw_data_to_hdf(complevel=9) [2min 54seconds]

Outcome: Default complevel=9 (Doubles the conversion time but load time isn't significantly deteriorated)
"""

from __future__ import division

import os
import copy
import re
import pandas as pd
import numpy as np
import countrycode as cc

from dataset import NBERFeenstraWTF 
from pyeconlab.util import 	from_series_to_pyfile, check_directory, recode_index, merge_columns, check_operations, update_operations, from_idxseries_to_pydict, \
							countryname_concordance, concord_data, random_sample, find_row
from pyeconlab.trade.classification import SITC

# - Data in data/ - #
this_dir, this_filename = os.path.split(__file__)
#DATA_PATH = check_directory(os.path.join(this_dir, "data"))
META_PATH = check_directory(os.path.join(this_dir, "meta"))

#-Concordances-#
from pyeconlab.country import iso3n_to_iso3c, iso3n_to_name 			#Why does this import prevent nosetests from running?				

class NBERFeenstraWTFConstructor(object):
	"""
	Data Constructor / Compilation Object for Feenstra NBER World Trade Data
	Years: 1962 to 2000
	Classification: SITC R2 L4 (Not Entirely Standard)
	Notes: Pre-1974 care is required for constructing intertemporally consistent data

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

		[3] I am not currently sure what these SITC codes are. I have requested further information from Robert Feenstra
			0021 	[Associated only with Malta]
			0023 	[Various Eastern European Countries and Austria]
			0024
			0025
			0031
			0035
			0039
			2829	[Assume: 282 NES. The MIT MediaLabs has this as “Waste and scrap metal of iron or steel” ]

		[4] There are currently 28 observations with no SITC4 codes. See issues_with_raw_data()

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
	[6] Construct a Dataset (NBERFeenstraWTF)
	[7] Supporting Functions
	[8] Generate Meta Data Files For Inclusion into Project Package (meta/)
	[9] Converters (hd5 Files etc.)

	Notes:
	------
	[1] There should only be ONE assignment in __init__ to the __raw_data attribute [Is there a way to enforce this?]
		Any modification prior to returning an NBERFeenstraWTF object should be carried out on "._dataset"
	[2] All Methods in this Class should operate on **NON** Indexed Data
	[3] This Dataset Requires ~25GB of RAM

	Future Work:
	-----------
	[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
	[2] When constructing meta/ data for inclusion in the package, it might be better to import from .dta files directly the required information
		For example. CountryCodes only needs to bring in a global panel of countrynames and then that can be converted to countrycodes
		[Update: This is currently not possible due to *.dta files being binary]
	[3] Move op_string work and turn it into a decorator function
	[4] To be more memory efficient we could enforce raw_data to be an HDFStore
	[5] Construct a BASE Constructor Class that contains generic methods (like IO)
	"""

	# - Attributes - #

	_exporters 			= None
	_importers 			= None 
	_country_list 		= None
	_dataset 			= None 									#Place holder for a constructed

	# - Dataset Attributes - #

	_name 				= u'NBERFeenstraWTF'
	source_web 			= u"http://cid.econ.ucdavis.edu/nberus.html"
	source_last_checked = np.datetime64('2014-07-04')
	complete_dataset 	= False 										#Make this harder to set
	years 				= []
	_available_years 	= xrange(1962,2000+1,1)
	_fn_prefix			= u'wtf'
	_fn_postfix			= u'.dta'
	_source_dir 		= None
	_raw_units 			= 1000
	_file_interface 	= [u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'unit', u'dot', u'value', u'quantity']
	
	# - Other Data in NBER Feenstra WTF -#
	_supp_data 			= dict
	
	# - Dataset Reference - #
	_mydataset_md5 		= u'36a376e5a01385782112519bddfac85e'
	__raw_data_hdf_fn 	= u'wtf62-00_raw.h5'
	__raw_data_hdf_yearindex_fn = u'wtf62-00_yearindex.h5'

	def set_fn_prefix(self, prefix):
		self._fn_prefix = prefix

	def set_fn_postfix(self, postfix):
		self._fn_postfix = postfix

	def __init__(self, source_dir, years=[], ftype='hdf', standardise=False, default_dataset=False, skip_setup=False, force=False, reduce_memory=True, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 		: 	Must contain the raw stata files (*.dta)
		years 			: 	Apply a Year Filter [Default: ALL]
		ftype 			: 	File Type ['dta', 'hdf'] [Default 'hdf' -> however it will generate on if not found from 'dta']
		standardise 	: 	Include Standardised Codes (Countries: ISO3C etc.)
		default_dataset : 	[True/False] Return a Default NBERFeenstraWTF Dataset 
								a. Collapse to Values ONLY
								b. Merge HongKong-China Adjustments
								c. Standardise
									-> Values in US$
									-> Add ISO3C Codes and Well Formatted CountryNames
									-> Include Indicator for Standard SITCR2 Codes ('sitcr2')
								c. Return NBERFeenstraWTF
									[year, importer, exporter, sitc4, value, sitcr2]
		skip_setup 		: 	[Testing] This allows you to skip __init__ setup of object to manually load the object with csv data etc. 
							This is mainly used for loading test data to check attributes and methods etc. 
		force 			: 	If not working with the full dataset you may enter force=True to run standardisation routines etc.
							[Warning: This will not return Intertemporally Consistent Concordances]
		"""
		#-Assign Source Directory-#
		self._source_dir 	= check_directory(source_dir) 	# check_directory() performs basic tests on the specified directory
		
		#-Parse Skip Setup-#
		if skip_setup==True:
			print "[INFO] Skipping Setup of NBERFeenstraWTFConstructor!"
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

		#-Construct Default Dataset-#
		if default_dataset == True:
			#-Copy raw_data to a flexible dataset attribute-# 					# This isn't very memory efficient, but allows preserving original data. 
			self._dataset = copy.deepcopy(self.__raw_data)
			#-Reduction/Collapse-#
			self.collapse_to_valuesonly(verbose=verbose) 						#This will remove unit, quantity
			#-Merge-#
			self.china_hongkongdata(years=years, verbose=verbose) 				
			self.adjust_china_hongkongdata(verbose=verbose)
			#-Adjust-#
			standardise = True 													#-Leave Standardisation to standardise option but ensure it is switched on

		#-Simple Standardization-#
		if standardise == True: 
			if verbose: print "[INFO] Running Interface Standardisation ..."
			self.standardise_data(force=force, verbose=verbose)
		
		#-Return NBERFeenstraWTF Object-#
		if default_dataset == True:
			if verbose: print "[INFO] Returning an NBERFeenstraWTF Data Object"
			return NBERFeenstraWTF(data=self._dataset, years=self.years, verbose=verbose)

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
	
	# - IO - #

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
		

	# - Raw Data Properties - #

	@property
	def raw_data(self):
		""" Raw Data Property to Return Private Attribute """ 
		try:
			return self.__raw_data 
		except: 																#Load from h5 file
			self.load_raw_from_hdf(years=self.years, verbose=False)
			return self.__raw_data

	def del_raw_data(self, force):
		""" Delete Raw Data """
		if force == True:
			self.__raw_data = None

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
			if self._supp_data[key] != None:
				items.append(key)
		return sorted(items)

	@property 
	def dataset(self):
		""" Dataset contains the Exportable Result to NBERFeenstraWTF """
		try:
			return self._dataset 
		except: 											#-Raw Data Not Yet Copied-#
			self._dataset = copy.deepcopy(self.__raw_data)
			return self._dataset


	def set_dataset(self, df, force=False):
		""" 
		Check if Dataset Exists Prior to Assignment
		Q: Is this ever going to be used?
		"""
		if type(self._dataset) == pd.DataFrame:
			if force == True:
				pass
			else:
				print "[WARNING] The dataset attribute has previously been set. To force the replacement use 'force'=True"
				return None
		self._dataset =  df 	#Should this make a copy?
		
	# ---------------------- #
	# - Supplementary Data - #
	# ---------------------- #

	def china_hongkongdata(self, years=[], return_dataset=False, verbose=True):
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

	# -------------------------- #
	# - Operations on Dataset  - #
	# -------------------------- #

	def adjust_china_hongkongdata(self, return_dataset=False, verbose=False):
		"""
		Replace/Adjust China and Hong Kong Data to account for China Shipping via Hong Kong
		This will merge in the Hong Kong / China Adjustments provided with the dataset for the years 1988 to 2000. 

		Arguments
		---------
		return_dataset 		: 	True/False [Default: False -> The Dataset is writen to self.dataset
		"""
		op_string = u'(adjust_raw_china_hongkongdata)'
		
		#-Check if Operation has been conducted-#
		if check_operations(self._dataset, op_string):
			#-Parse Return Option-#
			if return_dataset:
				return self._dataset
			else:
				return None

		#-Merge Settings-#
		if check_operations(self._dataset, u"collapse_to_valuesonly", verbose=False):
			on 			= 	[u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'dot']
		else:
		 	on 			= 	[u'year', u'icode', u'importer', u'ecode', u'exporter', u'sitc4', u'unit', u'dot']
		
		#-Note: Current merge_columns utility merges one column set at a time-#
		
		#-Values-#
		raw_value = self._dataset[on+['value']].rename(columns={'value' : 'value_raw'})
		try:
			supp_value = self._supp_data[u'chn_hk_adjust'][on+['value_adj']]
		except:
			raise ValueError("[ERROR] China/Hong Kong Data has not been loaded!")
		value = merge_columns(raw_value, supp_value, on, collapse_columns=('value_raw', 'value_adj', 'value'), dominant='right', output='final', verbose=verbose)

		#'Quantity' May not be available if collapse_to_valuesonly has been done etc.
		try:  															 
			#-Quantity-#
			raw_quantity = self._dataset[on+['quantity']]
			supp_quantity = self._supp_data[u'chn_hk_adjust'][on+['quantity']]
			quantity = merge_columns(raw_quantity, supp_quantity, on, collapse_columns=('quantity_x', 'quantity_y', 'quantity'), dominant='rights', output='final', verbose=verbose)
			#-Join Values and Quantity-#
			updated_raw_values = value.merge(quantity, how='outer', on=on)
		except:
			if verbose: print "[INFO] Quantity Information is not available in the current dataset\n"
			updated_raw_values = value 	#-Quantity Not Available-#

		report = 	u"# of Observations in Original Raw Dataset: \t%s\n" % (len(self._dataset)) +\
					u"# of Observations in Updated Dataset: \t\t%s\n" % (len(updated_raw_values))
		if verbose: print report

		#-Cleanup of Temporary Objects-#
		del raw_value, supp_value, value
		try:
			del raw_quantity, supp_quantity, quantity
		except:
			pass 	#-Quantity Merge Hasn't Taken Place-#

		#- Add Notes -#
		update_operations(updated_raw_values, op_string)

		#-Set Dataset to the Update Values-#
		self._dataset = updated_raw_values
		#-Parse Inplace Option-#
		if return_dataset == True:
			return self._dataset
		

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
		[1] Migrate set of standardisation methods to methods!
			change_units()
			add_iso3c()
			add_isocountrynames() 	#iso 
			add_sitcr2_official_marker()
		[2] Remove this and use subfunctions in __init__ to be more explicit
		"""
		op_string = u"(standardise_data)"
		#-Check if Operation has been conducted-#
		if check_operations(self._dataset, op_string): return None

		self.change_value_units(verbose=verbose) 			#Change Units to $'s
		self.add_iso3c(verbose=verbose)
		self.add_isocountrynames(verbose=verbose)
		self.add_sitcr2_official_marker(verbose=verbose) 	#Build SITCR2 Marker

		#- Add Operation to df attribute -#
		update_operations(self._dataset, op_string)



	# - Operations on Country Codes - #
	# ------------------------------- #

	fix_countryname_to_iso3n = 	{
									'Asia NES' 	: 896
									'Taiwan' 	: 158
									'Italy'		: 381
									'Norway' 	: 579
									'Switz.Liecht' : 757
									'Samoa'		: 882
									'Taiwan'	: 158
								}

	fix_countryname_to_iso3c = 	{
									'Asia NES' 	: '.'
									'Taiwan' 	: 'TWN'
									'Italy' 	: 'ITL'
									'Norway'	: 'NOR'
									'Switz.Liecht' : 'CHE'
									'Samoa'		: 'WSM'
									'Taiwan'	: 'TWN' 		#Note this is also 480 (Other Asia, NES)
								}

	def split_countrycodes(self, on='dataset', verbose=True):
		"""
		Split CountryCodes into components ('icode', 'ecode')
		XXYYYZ => UN-REGION [2] + ISO3N [3] + Modifier [1]

		Notes
		-----
		[1] Should this be done more efficiently? (i.e. over a single pass of the data) 
			Current timeit result: 975ms per loop for 1 year
		"""
		#-Check if Operation has been conducted-#
		op_string = u"(split_countrycodes)"
		if check_operations(self._dataset, op_string): return None

		# - Importers - #
		if verbose: print "Spliting icode into (iregion, iiso3n, imod)"
		self._dataset['iregion'] = self._dataset['icode'].apply(lambda x: int(x[:2]))
		self._dataset['iiso3n']  = self._dataset['icode'].apply(lambda x: int(x[2:5]))
		self._dataset['imod'] 	 = self._dataset['icode'].apply(lambda x: int(x[-1]))
		# - Exporters - #
		if verbose: print "Spliting ecode into (eregion, eiso3n, emod)"
		self._dataset['eregion'] = self._dataset['ecode'].apply(lambda x: int(x[:2]))
		self._dataset['eiso3n']  = self._dataset['ecode'].apply(lambda x: int(x[2:5]))
		self._dataset['emod'] 	 = self._dataset['ecode'].apply(lambda x: int(x[-1]))

		#- Add Operation to df attribute -#
		update_operations(self._dataset, op_string)


	def add_iso3c(self, verbose=False):
		""" 
		Add ISO3C codes to dataset

		This method uses the iso3n codes embedded in icode and ecode to add in iso3c codes
		This is the most reliable matching method. 
		However there are other ways by matching on countrynames etc.
		These concordances can be found in './meta'

		Alternatives
		------------
		[1] build_countrynameconcord_add_iso3ciso3n()

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
		op_string = u"(add_iso3c)"
		if check_operations(self._dataset, op_string): return None
		#-Core-#
		if not check_operations(self._dataset, u"(split_countrycodes"): 		#Requires iiso3n, eiso3n
			self.split_countrycodes(verbose=verbose)

		un_iso3n_to_iso3c = iso3n_to_iso3c(source_institution='un')
		#-Concord and Add a Column-#
		self._dataset['iiso3c'] = self._dataset['iiso3n'].apply(lambda x: concord_data(un_iso3n_to_iso3c, x, issue_error='.'))
		self._dataset['eiso3c'] = self._dataset['eiso3n'].apply(lambda x: concord_data(un_iso3n_to_iso3c, x, issue_error='.'))

		#-OpString-#
		update_operations(self._dataset, op_string)

	def add_isocountrynames(self, verbose=False):
		"""
		Add Standard Country Names

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
		if check_operations(self._dataset, op_string): return None

		#-Core-#
		if not check_operations(self._dataset, u"(split_countrycodes"): 		#Requires iiso3n, eiso3n
			self.split_countrycodes(verbose=verbose)

		un_iso3n_to_un_name = iso3n_to_name(source_institution='un') 
		#-Concord and Add a Column-#
		self._dataset['icountryname'] = self._dataset['iiso3n'].apply(lambda x: concord_data(un_iso3n_to_un_name, x, issue_error='.'))
		self._dataset['ecountryname'] = self._dataset['eiso3n'].apply(lambda x: concord_data(un_iso3n_to_un_name, x, issue_error='.'))

		#-WORKING HERE-#

		#-OpString-#
		update_operations(self._dataset, op_string)

	


	# - Operations on Product Codes - #
 	# ------------------------------- #	

	def collapse_to_valuesonly(self, verbose=False):
		"""
		Adjust Dataset For Export Values that are defined multiple times due to Quantity Unit Codes ('unit')
		Note: This will remove 'quantity', 'unit' ('dot'?)

		Questions
		---------
		1. Does this need to be performed before adjust_china_hongkongdata (as this might match multiple times!)?
		2. Write Tests
		"""
		#-Check if Operation has been conducted-#
		op_string = u"(collapse_to_valuesonly)"
		if check_operations(self._dataset, op_string): return None
		idx = ['year', 'icode',	'importer',	'ecode', 'exporter', 'sitc4']	
		# - Conduct Duplicate Analysis - #
		dup = self._dataset.duplicated(subset=idx)  
		if verbose:
			print "[INFO] Current Dataset Length: %s" % self._dataset.shape[0]
			print "[INFO] Current Number of Duplicate Entry's: %s" % len(dup[dup==True])
			print "[INFO] Deleting 'quantity', 'unit' as cannot aggregate quantity data in different units"
		del self._dataset['quantity']
		del self._dataset['unit']
		#-Collapse/Sum Duplicates-#
		self._dataset = self._dataset.groupby(by=idx).sum()
		self._dataset = self._dataset.reset_index() 			#Remove IDX For Later Data Operations
		if verbose:
			print "[INFO] New Dataset Length: %s" % self._dataset.shape[0]
		#- Add Operation to df attribute -#
		update_operations(self._dataset, op_string)

	def change_value_units(self, verbose=False):
		""" 
		Updates Values to $'s instead of 1000's of $'s' in Dataset
		"""
		#-OpString-#
		op_string = u"(change_value_units)"
		if check_operations(self._dataset, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Setting Values to be in $'s not %s$'s" % (self._raw_units)
		self._dataset['value'] = self._dataset['value'] * self._raw_units
		#-OpString-#
		update_operations(self._dataset, op_string)

	def add_sitcr2_official_marker(self, source_institution='un', verbose=False):
		""" 
		Add an Official SITCR2 Marker to Dataset
		source_institution 	: 	allows to specify where SITC() retrieves data [Default: 'un']
		"""
		#-OpString-#
		op_string = u"(add_sitcr2_official_marker)"
		if check_operations(self._dataset, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Adding SITC Revision 2 (Source='un') marker variable 'SITCR2'"
		sitc = SITC(revision=2, source_institution=source_institution)
		codes = sitc.get_codes(level=4)
		self._dataset['SITCR2'] = self._dataset['sitc4'].apply(lambda x: 1 if x in codes else 0)
		#-OpString-#
		update_operations(self._dataset, op_string)


	def add_productcode_levels(self, verbose=False):
		"""
		Split 'sitc4' into SITCL1, L2, and L3 Codes
		"""
		for level in [1,2,3]:
			self.add_productcode_level(level, verbose)

	def add_productcode_level(self, level, verbose=False):
		"""
		Add a Product Code for a specified level between 1 and 3 for 'sitc4'
		"""
		if level == 1:
			op_string = u"(add_productcode_level1)"
			if check_operations(self._dataset, op_string): return None
		elif level == 2:
			op_string = u"(add_productcode_level2)"
			if check_operations(self._dataset, op_string): return None
		elif level == 3:
			op_string = u"(add_productcode_level3)"
			if check_operations(self._dataset, op_string): return None
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
		update_operations(self._dataset, op_string)

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
		if check_operations(self._dataset, op_string): return None
		#-Core-#
		if verbose: print "[INFO] Identifying SITC Codes with A and X"
		self._dataset['SITCA'] = self._dataset['sitc4'].apply(lambda x: 1 if re.search("[aA]",x) else 0)
 		self._dataset['SITCX'] = self._dataset['sitc4'].apply(lambda x: 1 if re.search("[xX]",x) else 0)
		#-OpString-#
		update_operations(self._dataset, op_string)

	def intertemporal_consistent_productcodes(self, verbose=False):
		""" 
		Construct a set of ProductCodes that are Inter-temporally Consistent based around SITC Revision 2
		"""
		### -- Working Here --- ###
		raise NotImplementedError

	def intertemporal_consistent_productcodes_concord(self, verbose=False):
		"""
		Produce a concordance for inter-temporal consistent product codes for converting data post year 2000
		"""
		### -- Working Here --- ###
		raise NotImplementedError


	# ----------------------- #
	# - Construct a Dataset - #
	# ----------------------- #

	def to_nberfeenstrawtf(self, verbose=True):
		"""
		Construct NBERFeenstraWTF Object with Common Core Object Names
		Note: This is constructed from the ._dataset attribute

		Interface: ['year', iiso3c', 'eiso3c', 'sitc4', 'value', 'quantity']


		"""
		raise NotImplementedError

	# ----------------------------- #
	# - Supporting Functions 	  - #
	# ----------------------------- #

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

	# --------------------------------------------------------------- #
	# - Generate Meta Data Files For Inclusion into Project Package - #
	# - Note: These are largely for internal package construction 	- #
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
		[1] target_dir 	: 	target directory where files are to be written
							[Should specify REPO Location if updating REPO Files OR DATA_PATH if replace in Installed Package]
		[2] out_type 	: 	file type for results files 'csv', 'py' 
							[Default: 'py']

		Usage:
		-----
		Useful if NBER Feenstra's Dataset get's updated etc.

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
		

	def intertemporal_countrycodes(self, force=False, verbose=False):
		"""
		Construct a table of importer and exporter country codes by year
		Note: Works on self.raw_data
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Split Codes-#
		if not check_operations(self._dataset, u"(split_countrycodes"): 		#Requires iiso3n, eiso3n
			self.split_countrycodes(verbose=verbose)
		#-Core-#
		#-Importers-#
		table_iiso3n = self.raw_data[['year', 'importer', 'icode', 'iiso3n']].drop_duplicates().set_index(['importer', 'icode', 'year'])
		table_iiso3n = table_iiso3n.unstack(level='year')
		table_iiso3n.columns = table_iiso3n.columns.droplevel() 	#Removes Unnecessary 'iiso3n' label
		#-Exporters-#
		table_eiso3n = self.raw_data[['year', 'exporter', 'ecode', 'eiso3n']].drop_duplicates().set_index(['exporter', 'ecode', 'year'])
		table_eiso3n = table_eiso3n.unstack(level='year')
		table_eiso3n.columns = table_eiso3n.columns.droplevel() 	#Removes Unnecessary 'eiso3n' label
		return table_iiso3n, table_eiso3n


	def intertemporal_productcodes(self, force=False, verbose=False):
		"""
		Construct a table of productcodes by year
		Note: Works on self.raw_data
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Split Codes-#
		if not check_operations(self._dataset, u"(split_countrycodes"): 		#Requires iiso3n, eiso3n
			self.split_countrycodes(verbose=verbose)
		#-Core-#
		table_sitc4 = self.raw_data[['year', 'sitc4']].drop_duplicates()
		table_sitc4['code'] = 1
		table_sitc4 = table_sitc4.set_index(['sitc4', 'year']).unstack(level='year')
		#-Drop TopLevel Name in Columns MultiIndex-#
		table_sitc4.columns = table_sitc4.columns.droplevel() 	#Removes Unnecessary 'code' label
		return table_sitc4

	def write_metadata(self, target_dir='./meta', verbose=True):
		"""
		Write Files for ./meta in Excel Format

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


	# -------------- #
	# - Converters - #
	# -------------- #

	def convert_stata_to_hdf_yearindex(self, verbose=True):
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
		pd.set_option('io.hdf.default_format', 'table')
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		self.__raw_data_hdf_yearindex = hdf 									#SHould this be a filename rather than a Container?

		#-Convert Files -#					
		for year in self._available_years:
			dta_fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Converting file: %s to file: %s" % (dta_fn, hdf_fn)
			#pd.read_stata(dta_fn).to_hdf(hdf_fn, 'Y'+str(year))
			hdf.put('Y'+str(year), pd.read_stata(dta_fn), format='table')
			
		print hdf
		hdf.close()


	def convert_raw_data_to_hdf(self, verbose=True):
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
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		self.__raw_data_hdf = hdf
		pd.set_option('io.hdf.default_format', 'table')
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		hdf.put('raw_data', self.raw_data, format='table')

		print hdf
		hdf.close()


	# - Issues with Raw Data - #
	# ------------------------ #

	def issues_with_raw_data(self):
		"""
		Documents observed issues with the RAW DATA
		Note: This products files from where it is called

		[1] Missing SITC4 Codes (28 observations) -> './missing_sitc4.xlsx'
		"""
		codelength = self.raw_data['sitc4'].apply(lambda x: len(x))
		self.raw_data[codelength != 4].to_excel('missing_sitc4.xlsx')


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
		Generate a Global CountryName Concordance File for NBERFeenstraWTF Dataset

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