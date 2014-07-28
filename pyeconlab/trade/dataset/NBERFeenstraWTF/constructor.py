"""
NBERFeenstraWTF Constructer

Compile NBERFeenstra RAW data Files and Perform Basic Data Preparation Tasks

Tasks:
-----
	Basic Cleaning of Data 
	  [a] Add ISO3C country codes
	  [b] Add SITCR2 Markers

Conventions
-----------
	__raw_data 	: Should be an exact copy of the imported files and protected. 
	dataset 	: Contains the Modified Dataset

Returns
--------
Return Standardised Data in the Form of NBERFeenstraWTF
"""

import os
import copy
import pandas as pd
import numpy as np

from dataset import NBERFeenstraWTF 
from pyeconlab.util import from_series_to_pyfile, check_directory, recode_index, merge_columns, check_operations, update_operations 			#Reference requires installation!

# - Data in data/ - #
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = check_directory(os.path.join(this_dir, "data"))

class NBERFeenstraWTFConstructor(object):
	'''
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
		DOT 		:	Direction of trade (1=Data from importer, 2=Data from exporter)
		SITC 		: 	Standard International Trade Classification Revision 2
		ICode 		: 	Importer country code
		ECode 		: 	Exporter country code
		Importer 	: 	Importer country name
		Exporter 	: 	Exporter country name
		Unit 		: 	Units or measurement (see below)
		Year 		: 	4-digit year
 		Quantity 	: 	Quantity (only for years 1984 – 2000)
  		Value 		: 	Thousands of US dollars


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

		Types of Operations
		-------------------
		[1] Reduction/Collapse 	: 	This collapses data and applies a function like ADD to lines with the same idx 
									These need to happen BEFORE adjust methods
		[2] Merge 				: 	Merge methods that add data (such as Hong Kong adjusted data etc.)
		[3] Adjust 				: 	Adjust Methods alter the data but don't change it's length (spliting codes etc.)

		Order of Operations: 	Reduction/Collapse -> Merge -> Adjust

		Notes:
		------
		[1] icode & ecode are structured: XXYYYZ => UN-REGION [2] + ISO3N [3] + Modifier [1]
		[2] There should only be ONE assignment in __init__ to the __raw_data attribute [Is there a way to enforce this?]
			Any modification prior to returning an NBERFeenstraWTF object should be carried out on ._dataset
		[3] All Methods in this Class should operate on NON Indexed Data

		Future Work:
		-----------
			[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
	'''

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

	def set_fn_prefix(self, prefix):
		self._fn_prefix = prefix

	def set_fn_postfix(self, postfix):
		self._fn_postfix = postfix

	def __init__(self, source_dir, years=[], standardise=True, default_dataset=False, skip_setup=False, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 		: 	Must contain the raw stata files (*.dta)
		years 			: 	Apply a Year Filter [Default: ALL]
		standardise 	: 	Include Standardised Codes (Countries: ISO3C etc.)
		default_dataset : 	[True/False] Return a Default NBERFeenstraWTF Dataset 
								a. Collapse to Values ONLY
								b. Merge HongKong-China Adjustments
								c. Standardise
									-> Values in US$
									-> Add CountryCodes in ISO3C
									-> Include Indicator for Standard SITCR2 Codes ('sitcr2')
								c. Return NBERFeenstraWTF
									[year, importer, exporter, sitc4, value, sitcr2]
		skip_setup 		: 	[Testing] This allows you to skip __init__ setup of object to manually load the object with csv data etc. 
							This is mainly used for loading test data to check attributes and methods etc. 
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
		
		# - Fetch Raw Data for Years - #
		self.years 			= years
		self.__raw_data 	= pd.DataFrame() 				#PRIVATE Attribute of the Class
		for year in self.years:
			fn = self._source_dir + self._fn_prefix + str(year)[-2:] + self._fn_postfix
			if verbose: print "Loading Year: %s from file: %s" % (year, fn)
			self.__raw_data = self.__raw_data.append(pd.read_stata(fn))

		#-Copy raw_data to a flexible dataset attribute-#
		self._dataset = copy.deepcopy(self.__raw_data)

		#-Construct Default Dataset-#
		if default_dataset == True:
			#-Reduction/Collapse-#
			self.collapse_to_valuesonly(verbose=verbose)
			#-Merge-#
			self.china_hongkongdata(years=years, verbose=verbose)
			self.adjust_china_hongkongdata(verbose=verbose)
			#-Adjust-#
			#-Leave Standardisation to standardise option-#

		#-Simple Standardization-#
		if standardise == True: 
			if verbose: print "[INFO] Running Interface Standardisation ..."
			self.standardise_data(verbose=False)
		
		#-Return NBERFeenstraWTF Object-#
		if default_dataset == True:
			#return NBERFeenstraWTF(data=self._dataset, years=self.years, verbose=verbose)
			pass

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
	
	def from_csv(self, fl, test_data=True, verbose=True):
		""" Load Data from CSV into self.__raw_data """
		fl = self._source_dir + fl
		if verbose: print "[WARNING] Loading data from %s into __raw_data" % fl
		self.__raw_data = pd.read_csv(fl)
		self.test_data = test_data

	def from_df(self, df, test_data=True, verbose=True):
		""" Load Data from Pandas DataFrame into self.__raw_data """
		if verbose: print "[WARNING] Loading data from dataframe into __raw_data" % fl
		self.__raw_data = df
		self.test_data = test_data

	# - Raw Data Properties - #

	@property
	def raw_data(self):
		""" Raw Data Property to Return Private Attribute """ 
		return self.__raw_data

	@property
	def exporters(self):
		""" Returns List of Exporters """
		if self._exporters == None:
			self._exporters = list(self.__raw_data['exporter'].unique())
			self._exporters.sort()
		return self._exporters	

	def global_exporter_list(self):
		"""
		Return Global Sorted Unique List of Exporters
		Useful as Input to Concordances such as NBERFeenstraExporterToISO3C

		To Do:
		------
			[1] Should I write an Error Decorator? 
		"""
		if self.complete_dataset == True:
			return self.exporters
		else:
			raise ValueError("Raw Dataset must be complete - currently %s years have been loaded" % self.years)

	@property
	def importers(self):
		""" Returns List of Importers """
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
		self._dataset = df
		
	# - Supplementary Data - #

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
		"""
		# - Attributes of China Hong-Kong Adjustment - #
		fn_prefix 	= u'china_hk'
		fn_postfix 	= u'.dta'
		available_years = xrange(1988, 2000 + 1)
		key 		= u'chn_hk_adjust'
		
		#- Parse Year Filter - #
		if years == []:
			years = available_years
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

	# - Operations on Dataset  - #

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
		on 			= list(self._dataset.columns[0:8])
		#-Note: Current merge_columns utility merges one column set at a time-#
		#-Merge over the first 8 Columns for Value and Quantity-#
		#-Values-#
		raw_value = self._dataset[on+['value']].rename(columns={'value' : 'value_raw'})
		try:
			supp_value = self._supp_data[u'chn_hk_adjust'][on+['value_adj']]
		except:
			raise ValueError("[ERROR] China/Hong Kong Data has not been loaded!")
		value = merge_columns(raw_value, supp_value, on, collapse_columns=('value_raw', 'value_adj', 'value'), dominant='right', output='final', verbose=verbose)
		#-Quantity-#
		raw_quantity = self._dataset[on+['quantity']]
		supp_quantity = self._supp_data[u'chn_hk_adjust'][on+['quantity']]
		quantity = merge_columns(raw_quantity, supp_quantity, on, collapse_columns=('quantity_x', 'quantity_y', 'quantity'), dominant='right', output='final', verbose=verbose)
	
		#-Join Values and Quantity-#
		updated_raw_values = value.merge(quantity, how='outer', on=on)
		
		report = 	u"# of Observations in Original Raw Dataset: \t%s\n" % (len(self._dataset)) +\
					u"# of Observations in Updated Dataset: \t\t%s\n" % (len(updated_raw_values))
		if verbose: print report

		#-Cleanup of Temporary Objects-#
		del raw_value, supp_value, value
		del raw_quantity, supp_quantity, quantity

		#- Add Notes -#
		update_operations(updated_raw_values, op_string)

		#-Set Dataset to the Update Values-#
		self._dataset = updated_raw_values
		#-Parse Inplace Option-#
		if return_dataset == True:
			return self._dataset
		

	# - Generate Supporting Files for a data/ folder - #

	def generate_global_info(self, target_dir=DATA_PATH, out_type='py', verbose=False):
		"""
		Construct Global Information About the Dataset 
		Automatically import ALL data and Construct Unique:
			[1] Country List
			[2] Exporter List
			[3] Importer List

		Parameters:
		-----------
		[1] target_dir 	: 	target directory where files are to be written
							[Default: writes files to the NBERFeenstraWTF subpackage]
		[2] out_type 	: 	file type for results files 'csv', 'py' 
							[Default: 'py']

		Usage:
		-----
		Useful if NBER Feenstra's Dataset get's updated etc.

		Future Work:
		------------
		[1] Update so that the new files are saved in the package location, not a local folder
			Currently this will produce the files, that will need to be relocated to package
		"""
		# - Check if Dataset is Complete for Global Info Property - #
		if self.complete_dataset != True:
			raise ValueError("Dataset must be complete. Try running the constructor without defining years=[]")
		if out_type == 'csv':
			# - Exporters - #
			pd.DataFrame(self.exporters, columns=['exporter']).to_csv(target_dir + 'exporters_list.csv', index=False)
			# - Importers - #
			pd.DataFrame(self.importers, columns=['importer']).to_csv(target_dir + 'importers_list.csv', index=False)
			# - Country List - #
			pd.DataFrame(self.country_list, columns=['country_list']).to_csv(target_dir + 'countryname_list.csv', index=False)
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
		# - Summary - #
		if verbose: 
			print "[INFO] Writing Exporter, Importer, and CountryLists to %s files in location:" % out_type
			print target_dir

	## - Clean Data Tasks - ##

	def standardise_data(self,verbose=False):
		'''
		Run Appropriate Standardization over the Dataset
		
		Actions
		-------
			[1] Trade Values in $'s 
			[2] Countries to ISO3C Codes
			[3] Marker for Standard SITC Revision 2 Codes

		Notes
		-----
			[1] Raw Dataset has Non-Standard SITC rev2 Codes 
		'''
		op_string = u"(standardise_data)"
		#-Check if Operation has been conducted-#
		if check_operations(self._dataset, op_string): return None

		#-Change Units to $'s-#
		self._dataset['value'] = self._dataset['value'] * 1000
		#-Update Country Names-#
		self.split_countrycodes(verbose=verbose) 		#Note: This won't run if it has run already#

		###---WORKING HERE---####

		#- Add Operation to df attribute -#
		update_operations(self._dataset, op_string)


	def split_countrycodes(self, verbose=True):
		"""
		Split CountryCodes into components ('icode', 'ecode')
		XXYYYZ => UN-REGION [2] + ISO3N [3] + Modifier [1]

		Notes:
		-----
		[1] Should this be done more efficiently? (i.e. over a single pass of the data) 
			Current timeit result: 975ms per loop for 1 year
		"""
		#-Check if Operation has been conducted-#
		op_string = u"(split_countrycodes)"
		if check_operations(self._dataset, op_string): return None

		# - Importers - #
		if verbose: print "Spliting icode into (iregion, iiso3n, imod)"
		self._dataset['iregion'] = self._dataset['icode'].apply(lambda x: x[:2])
		self._dataset['iiso3n']  = self._dataset['icode'].apply(lambda x: x[2:5])
		self._dataset['imod'] 	 = self._dataset['icode'].apply(lambda x: x[-1])
		# - Exporters - #
		if verbose: print "Spliting ecode into (eregion, eiso3n, emod)"
		self._dataset['eregion'] = self._dataset['ecode'].apply(lambda x: x[:2])
		self._dataset['eiso3n']  = self._dataset['ecode'].apply(lambda x: x[2:5])
		self._dataset['emod'] 	 = self._dataset['ecode'].apply(lambda x: x[-1])

		#- Add Operation to df attribute -#
		update_operations(self._dataset, op_string)

	def collapse_to_valuesonly(self, verbose=False):
		"""
		Adjust Dataset For Export Values that are defined multiple times due to Quantity Unit Codes ('unit')
		Note: This will remove 'quantity', 'unit' ('dot'?)

		Questions
		---------
		1. Does this need to be performed before adjust_china_hongkongdata (as this might match multiple times!)?
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

	# - Construct a Dataset - #

	def to_nberfeenstrawtf(self, verbose=True):
		"""
		Construct NBERFeenstraWTF Object with Common Core Object Names
		Note: This is constructed from the ._dataset attribute

		Interface: ['year', iiso3c', 'eiso3c', 'sitc4', 'value', 'quantity']


		"""
		raise NotImplementedError