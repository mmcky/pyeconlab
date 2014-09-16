"""
Constructor for Working with CEPII/BACI Data

Files
-----
baciHS_YYYY.rar 	where HS=92,96,02 and YYYY=full year

Internal Variables
------------------
	t 	: year 
	hs6 : hs6 digit product code 
	i 	: exporter 
	j 	: importer 
	v 	: value, in thousands of US dollars
	q 	: quantity, in tons
	a 	: start_year (?)

Supplimentary Files
-------------------
HS92
~~~~
[1] country_code_baci92.csv
[2] product_code_baci92.csv
[3] reporter_reliability_92.rar 
[4] zero_92.rar

HS96
~~~~
[1] country_code_baci96.csv
[2] product_code_baci96.csv
[3] reporter_reliability_96.rar 
[4] zero_96.rar

HS02
~~~~
[1] country_code_baci02.csv
[2] product_code_baci02.csv
[3] reporter_reliability_02.rar 
[4] zero_02.rar

Notes
-----
[1] BACI has a few different version based on HS system, which may influence the BACI meta data object
"""

import re
import warnings
import string
import pandas as pd
import numpy as np

from .base import BACI
from .dataset import BACITradeData, BACIExportData, BACIImportData
from pyeconlab.trade.dataset import CPTradeData, CPExportData, CPImportData

from pyeconlab.country import ISO3166
from pyeconlab.util import check_directory, check_operations, update_operations, from_idxseries_to_pydict, concord_data

class BACIConstructor(BACI):
	"""
	BACI Data Constructor

	Inheritance
	-----------
		[1] BACI 			: 	Provides Meta Data on CEPII Dataset

	Country Codes 
	-------------
	[1] Not all country codes are the current ISO3166 iso3n values.
		'France' = 251 in Baci; while ISO3166 records 'France' = 250
		Therefore use BACI country concordance to assign iso3c values

	Notes
	-----
	[1] When should standard_names be implimented (at the beginning or at the end?)
		Beginning: update all native imports, but a bit easier to read in the programming
		End: all baci files merge natively untouched. Could write a merge routine to undertake this approach as a check against using standard_names

	Questions
	---------
	[1] Should self.raw_data have i,j etc rather than standard_names if it is to be untouched.
	"""

	#-Constructor Meta Data/Attributes-#

	#-Protected Attributes-#
	__raw_data 	= pd.DataFrame
	__source_dir 	= str
	
	#-Flexible Attributes-#
	dataset 		= pd.DataFrame
	data_type 			= str
	name 			= str 
	classification = str 
	revision 		= str 
	years 			= list 
	notes 			= str
	complete_dataset = bool
	standard_names 	= bool
	operations 		= str

	#-Specific Attributes to BACIConstructor-#

	product_datafl_fixed = bool 
	country_datafl_fixed = bool


	def __init__(self, source_dir, source_classification, ftype='csv', years=[], standard_names=True, skip_setup=False, reduce_memory=False, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 				: 	Must contain the raw csv files
		source_classification 	: 	Type of Source Files to Load ['HS92', 'HS96', 'HS02']
		source_revision 		: 	1992, 1996, 2002
		years 					: 	Apply a Year Filter [Default: ALL]
		ftype 					: 	File Type ['rar', 'csv', hdf']
		skip_setup 				: 	[Testing] This allows you to skip __init__ setup of object to manually load the object with csv data etc. 
									This is mainly used for loading test data to check attributes and methods etc. 
		reduce_memory			: 	This will delete self.__raw_data after initializing self._dataset with the raw_data
									[Warning: This will render properties that depend on self.__raw_data inoperable]
									Usage: Useful when building datasets to be more memory efficient as the operations don't require a record of the original raw_data
									[Default: False] Only Saves ~?GB of RAM
		
		Future Work
		-----------
		[1] Should I add a hdf_fn='' option for specifying a h5 file rather than using the internal defaults?
		"""
		#-Assign Source Directory-#
		self.__source_dir 	= check_directory(source_dir) 		#check_directory() performs basic tests on the specified directory

		#-Source Attributes-#
		self.source_revision = self.source_revision[source_classification] 	#Overright with Appropriate Revision based on source_classification

		#-Assign Default Attributes-#
		self.name 			= u"BACI Dataset"
		self.data_type 		= u"trade"
		self.classification = source_classification
		self.revision 		= source_classification[-2:] 		#Last two digits	
		self.notes 			= ""
		self.operations 	= u"" 
		self.complete_dataset = False

		#-Country, Product Source File Fixed Indicator-#
		self.product_datafl_fixed = False 						#Should this be more sophisticated, this is a constructor so probably not
		self.country_datafl_fixed = False

		#-Parse Years-#
		if verbose: print "[INFO] Fetching BACI Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True						# This forces object to be imported based on the whole dataset
			years = self.source_available_years[self.classification] 	
		#-Assign to Attribute-#
		self.years = years 		

		#-Parse Skip Setup-#
		if skip_setup == True:
			print "[INFO] Skipping Setup of BACI Constructor!"
			self.__raw_data 	= None 										#Allows to be assigned later on
			return None

		# - Fetch Raw Data for Years - #
		if ftype == 'rar':
			self.load_raw_from_rar(verbose=verbose)
		elif ftype == 'csv':
			self.load_raw_from_csv(standard_names=False, verbose=verbose)
		elif ftype == 'hdf':
			try:
				self.load_raw_from_hdf(years=years, verbose=verbose)
			except:
				print "[INFO] Your source directory: %s does not contain h5 version.\nStarting to compile one now ...." % self.source_dir
				self.load_raw_from_csv(standard_names=False, verbose=verbose)
				self.convert_raw_data_to_hdf(verbose=verbose) 				#Compute hdf file for next load
				self.convert_raw_data_to_hdf_yearindex(verbose=verbose)		#Compute Year Index Version Also
		else:
			raise ValueError("ftype must be 'rar', 'csv', or 'hdf'")

		#-Reduce Memory-#
		if reduce_memory:
			self.dataset = self.__raw_data 									#Saves ~2Gb of RAM (but cannot access raw_data)
			self.__raw_data = None
		else:
			self.dataset = self.__raw_data.copy(deep=True) 					#[Default] pandas.DataFrame.copy(deep=True) is much more efficient than copy.deepcopy()

		#-Standard Names Option-#
		self.standard_names = standard_names
		if self.standard_names:
			self.use_standard_column_names(self.dataset, verbose=verbose)


	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years)								+ \
				 "Complete Dataset: %s\n" % (self.complete_dataset) 		+ \
				 "# Raw Observations: %s\n" % (self.__raw_data.shape[0]) 	+ \
				 "# Dataset Observations: %s\n" % (self.dataset.shape[0]) 	+ \
				 "Source Last Checked: %s\n" % (self.source_last_checked)
		return string
	
	#-----------------------------------#
	#-Properties (Protected Attributes)-#
	#-----------------------------------#

	@property
	def raw_data(self):
		""" Raw Data Property to Return a Copy of the Private Attribute """ 
		try:
			return self.__raw_data.copy(deep=True)  							#Always Return a Copy
		except: 																#Load from h5 file (quickest Load Times)
			self.load_raw_from_hdf(years=self.years, verbose=False)
			return self.__raw_data.copy(deep=True)

	def del_raw_data(self, force=False):
		""" Delete Raw Data """
		if force==True:
			del self.__raw_data

	@property
	def source_dir(self):
		return self.__source_dir

	#----#
	#-IO-#
	#----#

	def load_raw_from_csv(self, standard_names=False, deletions=True, verbose=False):
		""" 
		Load Raw Data from CSV Files [Main Entry Point for Raw Data]

		standard_names : apply standard names [True/False] using interface dictionary
		deletions : apply deletions attribute 

		Questions
		---------
		[1] Should this be moved to Generic Constructor Class? 
		"""
		if verbose: print "[INFO] Loading RAW [.csv] Files from: %s" % (self.source_dir)
		self.__raw_data = pd.DataFrame()
		for year in self.years:
			fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + str(year) + '.csv'
			if verbose: print "[INFO] Loading Year: %s from file: %s" % (year, fn)
			self.__raw_data = self.__raw_data.append(pd.read_csv(fn, data_type={'hs6' : str}))
		self.__raw_data = self.__raw_data.reset_index() 					#Otherwise Each year has repeated obs numbers
		del self.__raw_data['index']
		if deletions:
			for item in self.source_deletions[self.classification]:
				if verbose: print "[DELETING] Column: %s" % item
				del self.__raw_data[item]
		if standard_names: 														#Current Default is 'False' to keep raw_data in it's raw state
			self.use_standard_column_names(self.__raw_data)

	def load_raw_from_hdf(self, years=[], verbose=False):
		"""
		Load HDF Version of RAW Dataset from a source_directory
		Note: 	To construct your own hdf version requires to initially load from BACI supplied RAW dta files
				Then use Constructor method ``convert_source_csv_to_hdf()``

		Questions:
		[1] Should this be moved to Generic Constructor Class?
		"""
		self.__raw_data = pd.DataFrame() 
		print years
		if years == [] or years == self.source_available_years[self.classification]:
			fn = self.source_dir + self.raw_data_hdf_fn[self.classification]
			if verbose: print "[INFO] Loading RAW DATA from %s" % fn
			self.__raw_data = pd.read_hdf(fn, key='raw_data')
		else:
			fn = self.source_dir + self.raw_data_hdf_yearindex_fn[self.classification] 
			for year in years:
				if verbose: print "[INFO] Loading RAW DATA for year: %s from %s" % (year, fn)
				self.__raw_data = self.__raw_data.append(pd.read_hdf(fn, key='Y'+str(year)))

	def load_country_data(self, fix_source=True, standard_names=True, verbose=True):
		"""
		Load Country Classification/Concordance File From Archive
		Note: [1] Write a wrapper for self.classification selection?
		"""
		if fix_source and self.country_datafl_fixed == False:
			if self.classification == "HS92" or self.classification == "HS96":
				self.fix_country_code_baci9296(verbose=verbose)
			if self.classification == "HS02":
				self.fix_country_code_baci02(verbose=verbose)
		if self.country_datafl_fixed == False and self.classification == "HS02":
			print "[WARNING] Has the country_code_baci02 data been adjusted in the source_dir!"
		fn = self.source_dir + self.country_data_fn[self.classification]
		self.country_data = pd.read_csv(fn)
		if standard_names:
			self.country_data.rename(columns={'i' : 'iso3n', 'iso3' : 'iso3c'}, inplace=True)

	def load_product_data(self, fix_source=True, standard_names=True, verbose=False):
		"""
		Load Product Code Classification File from Archive
		"""
		if fix_source and self.product_datafl_fixed == False:
			if self.classification == "HS92":
				self.fix_product_code_baci92(verbose=verbose)
			if self.classification == "HS96":
				self.fix_product_code_baci96(verbose=verbose)
			if self.classification == "HS02":
				self.fix_product_code_baci02(verbose=verbose)
		if self.product_datafl_fixed == False and self.classification == "HS02":
			print "[WARNING] Has the product_code_baci02 data been adjusted in the source_dir!"
		fn = self.source_dir + self.product_data_fn[self.classification]
		self.product_data = pd.read_csv(fn, data_type={'Code' : object})
		if standard_names:
			self.use_standard_column_names(self.product_data)

	def use_standard_column_names(self, df, verbose=True):
		"""
		Use interface attribute to Adjust Columns to use Standard Names (inplace=True)
		"""
		opstring = u"(use_standard_column_names)"
		if verbose:
			for item in df.columns:
				try: print "[CHANGING] Column: %s to %s" % (item, self.source_interface[item])
				except: pass 																#Passing Items not Converted by self.source_interface
		self.standard_names = True
		df.rename(columns=self.source_interface, inplace=True)
		#-Update Operations Attribute-#
		update_operations(self, opstring)

	#------------#
	#-Conversion-#
	#------------#

	def convert_raw_data_to_hdf(self, key='raw_data', format='fixed', hdf_fn='', verbose=True):
		""" 
		Convert Raw Data to HDF
		Note: this currently just converts whatever is contained in raw_data
		Future Work
		-----------
		[1] Add a year filter and name the file accordingly
		"""
		if hdf_fn == '':
			hdf_fn = self.source_dir + self.raw_data_hdf_fn[self.classification] 	#This default is the entire dataset for any given classification
		if verbose: print "[INFO] Writing raw_data to %s" % hdf_fn
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		hdf.put(key, self.raw_data, format=format)
		if verbose: print hdf
		hdf.close()
	
	def convert_raw_data_to_hdf_yearindex(self, format='fixed', hdf_fn='', verbose=True):
		""" 
		Convert Raw Data to HDF File Indexed by Year
		Note: This compute a list of unique years from self.__raw_data
		"""
		if hdf_fn == '': 
			hdf_fn = self.source_dir + self.raw_data_hdf_yearindex_fn[self.classification] 	#This default is the entire dataset for any given classification
		if verbose: print "[INFO] Writing raw_data to %s" % hdf_fn
		#-Construct HDF File-#
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		if self.standard_names == True:
			yid = 'year'
		else:
			yid = 't'
		for year in self.raw_data[yid].unique():
			hdf.put('Y'+str(year), self.raw_data.loc[self.raw_data[yid] == year], format=format) 	
		if verbose: print hdf
		hdf.close()

	def convert_csv_to_hdf_yearindex(self, years=[], format='fixed', hdf_fn='', verbose=True):
		""" 
		Convert CSV Files to HDF File Indexed by Year
		year 	: 	apply a year filter
		"""
		if years == []:
			years = self.source_available_years[self.classification]
		#-Setup HDF File-#
		if hdf_fn == '':
			hdf_fn = self.source_dir + self.raw_data_hdf_yearindex_fn[self.classification]
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		#-Convert Years-#
		for year in years:
			csv_fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + str(year) + '.csv'
			if verbose: print "[INFO] Converting file: %s to file: %s" % (csv_fn, hdf_fn)
			hdf.put('Y'+str(year), pd.read_csv(csv_fn, data_type={'hs6' : str}), format=format)
		if verbose: print hdf
		hdf.close()
		return hdf_fn

	#-------------------#
	#-Fix Source Issues-#
	#-------------------#

	def fix_country_code_baci(self, verbose=True):
		"""
		Fix Source Country Code File Based on Classification
		"""
		opstring = u"(fix_country_code)"
		if self.classification == "HS92":
			self.fix_country_code_baci9296(verbose=verbose)
		elif self.classification == "HS96":
			self.fix_country_code_baci9296(verbose=verbose)
		elif self.classification == "HS02":
			self.fix_country_code_baci02(verbose=verbose)
		else:
			raise ValueError("Invalid Classification: %s" % self.classification)
		update_operations(self, opstring)

	def fix_country_code_baci9296(self, verbose=True):
		""" 
		Fix issue with country_code_baci92 or country_code_baci96 csv file
		"""
		if verbose: print "[INFO] Fixing original %s country data file in source_dir: %s" % (self.classification, self.source_dir)
		if self.classification != "HS92" and self.classification != "HS96":
			raise ValueError("This method only runs on HS92 or HS96 Data")
		fn = self.country_data_fn[self.classification]
		f = open(self.source_dir + fn, 'r')
		#-Adjust Filename-#
		fn,ext = fn.split(".")
		fn = fn + "_adjust" + "." + ext
		nf = open(self.source_dir + fn, 'w')
		#-Core-#
		for idx, line in enumerate(f):
			line = filter(lambda x: x in string.printable, line)
			line = line.replace("?", "")
			nf.write(line)
		#-Close Files-#
		f.close()
		nf.close()
		#-DropDuplicates-#
		df = pd.read_csv(self.source_dir+fn)
		init_shape = df.shape
		df = df.drop_duplicates()
		df.to_csv(self.source_dir+fn, index=False)
		if verbose: print "[INFO] Dropping (%s) Duplicates Found in country codes file: %s" % (init_shape[0] - df.shape[0], self.country_data_fn[self.classification])
		#-Update File List to use adjusted File-#
		if verbose: print "[INFO] Replacing internal reference from: %s to: %s" % (self.country_data_fn[self.classification], fn)
		self.country_data_fn[self.classification] = fn
		self.country_datafl_fixed = True

	def fix_country_code_baci02(self, verbose=True):
		""" 
		Fix issue with country_code_baci02 csv file
		"""
		if verbose: print "[INFO] Fixing original HS02 country data file in source_dir: %s" % self.source_dir
		if self.classification != "HS02":
			raise ValueError("This method only runs on HS02 Data")
		fn = self.country_data_fn["HS02"]
		f = open(self.source_dir + fn, 'r')
		#-Adjust Filename-#
		fn,ext = fn.split(".")
		fn = fn + "_adjust" + "." + ext
		nf = open(self.source_dir + fn, 'w')
		#-Core-#
		for idx, line in enumerate(f):
			line = filter(lambda x: x in string.printable, line)
			line = line.replace("?", "")
			match = re.match("\"(.*)\"", line)
			if match:
				nwl = match.group(1)
				nwl = nwl.replace("\"\"", "\"")
				nwl += "\n"
			else:
				nwl = "%s,%s,\"%s\",\"%s\",%s" % tuple(line.split(","))
			nf.write(nwl)
		#-Close Files-#
		f.close()
		nf.close()
		#-DropDuplicates-#
		df = pd.read_csv(self.source_dir+fn)
		init_shape = df.shape
		df = df.drop_duplicates()
		df.to_csv(self.source_dir+fn, index=False)
		if verbose: print "[INFO] Dropping (%s) Duplicates Found in country codes file: %s" % (init_shape[0] - df.shape[0], self.country_data_fn["HS02"])
		#-Update File List to use adjusted File-#
		if verbose: print "[INFO] Replacing internal reference from: %s to: %s" % (self.country_data_fn["HS02"], fn)
		self.country_data_fn["HS02"] = fn
		self.country_datafl_fixed = True

	#-ProductCode File Fixes-#

	def fix_product_code_baci92(self, verbose=True):
		"""
		Fix issues with the product_code_baci92.csv file
		"""
		if verbose: print "[INFO] Fixing original HS92 product data file in source_dir: %s" % self.source_dir
		fn = self.product_data_fn["HS92"]
		df = pd.read_csv(self.source_dir + fn)
		df.columns = ["Code", "Description"]
		#-Update FileName-#
		fn,ext = fn.split(".")
		fn = fn + "_adjust" + "." + ext
		df.to_csv(self.source_dir + fn, index=False, quoting=True)
		#-Update File List to use adjusted File-#
		if verbose: print "[INFO] Replacing internal reference from: %s to: %s" % (self.product_data_fn["HS92"], fn)
		self.product_data_fn["HS92"] = fn
		self.product_datafl_fixed = True

	def fix_product_code_baci96(self, verbose=True):
		"""
		Fix issues with product_code_baci96.csv file
		"""
		if verbose: print "[INFO] Fixing original HS96 product data file in source_dir: %s" % self.source_dir
		if self.classification != "HS96":
			raise ValueError("This method only runs on HS96 Data")
		fn = self.product_data_fn["HS96"]
		f = open(self.source_dir + fn, 'r')
		#-Adjust Filename-#
		fn,ext = fn.split(".")
		fn = fn + "_adjust" + "." + ext
		nf = open(self.source_dir + fn, 'w')
		for idx, line in enumerate(f):
			if idx == 0:
				nf.write("\"Code\",\"Description\"\n")
				continue
			code = re.match("([0-9]*);?", line).group(1) 											#look for productcodes
			rest = line.lstrip(code+";")
			rest = rest.replace("\"", "")
			rest = rest.rstrip("\n")
			line = "\"%s\",\"%s\"" % (code, rest)
			nf.write(line + "\n")
		#-Close Files-#
		f.close()
		nf.close()
		#-Update File List to use adjusted File-#
		if verbose: print "[INFO] Replacing internal reference from: %s to: %s" % (self.product_data_fn["HS96"], fn)
		self.product_data_fn["HS96"] = fn
		self.product_datafl_fixed = True

	def fix_product_code_baci02(self, verbose=True):
		"""
		Fix issue with product_code_baci02 csv file
		"""
		if verbose: print "[INFO] Fixing original HS02 product data file in source_dir: %s" % self.source_dir
		if self.classification != "HS02":
			raise ValueError("This method only runs on HS02 Data")
		fn = self.product_data_fn["HS02"]
		f = open(self.source_dir + fn, 'r')
		#-Adjust Filename-#
		fn,ext = fn.split(".")
		fn = fn + "_adjust" + "." + ext
		nf = open(self.source_dir + fn, 'w')
		for idx, line in enumerate(f):
			line = re.match("^\"(.*)\"$", line).group(1) 					#Unwrap extra "'s
			line = line.replace('\"\"', '\"') 								#Remove Double Quoting
			#-Fix for Code Column-#
			if idx == 0:
				line = line.lstrip('Code')
				line = '\"Code\"' + line
			else:
				try:
					code = re.search("^([0-9]*),", line).group(1)
				except:
					continue 												#Trailing White Spaces
				line = line.lstrip(code)
				line = '\"' + code + '\"' + line
			nf.write(line + "\n")
		#-Close Files-#
		f.close()
		nf.close()
		#-Update File List to use adjusted File-#
		if verbose: print "[INFO] Replacing internal reference from: %s to: %s" % (self.product_data_fn["HS02"], fn)
		self.product_data_fn["HS02"] = fn
		self.product_datafl_fixed = True

	#-----------------------#
	#-Operations on Dataset-#
	#-----------------------#

	def add_country_iso3c(self, remove_iso3n=False, dropna=False, drop_special=(False, ['NTZ']), verbose=True):
		"""
		Add CountryNames to ISO3N Codes

		remove_iso3n 	: 	remove iso3n columns
		dropna 			: 	drop countries in the concordance that are np.nan() 	
							[Default: False. Care must be given when dropping as it may influence exporter, importer collapses]
		drop_special 	: 	drop special tuple 3-digit codes such as NTZ = Neutral Zone
							[Note: First Item is True/False to see if drop_special should be processed]

		Notes
		-----
		[1] Check these against the CountryNames Concordance File to Ensure that None of them are Countries
		dropna=True
		~~~~~~~~~~~
		[1] EISO3N Codes Dropped: 
			[10, 74, 80, 129, 239, 275, 290, 334, 336, 471, 473, 492, 499, 527, 531, 534, 535, 568, 577, 581,636, 637, 688, 728, 729, 807, 837, 838, 839, 879, 899]
		[2] IISO3N Codes Dropped: 
			[10, 74, 80, 129, 221, 239, 275, 290, 334, 336, 471, 473, 492, 499, 527, 531, 534, 535, 568, 577, 581, 636, 637, 688, 697, 728, 729, 807, 837, 838, 839, 879, 899]
		"""
		edrop, idrop, spdrop = 0,0,0
		init_obs = self.dataset.shape[0]
		#-Exporter-#
		self.dataset = self.dataset.merge(self.country_data[['iso3n', 'iso3c']], how='left', left_on=['eiso3n'], right_on=['iso3n'])
		del self.dataset['iso3n'] 																											#Remove Merge Key
		self.dataset.rename(columns={'iso3c' : 'eiso3c'}, inplace=True)
		if dropna:
			print "[INFO] Removing Units with eiso3c == np.nan"
			edrop = len(self.dataset[self.dataset.eiso3c.isnull()])
			print "[Deleting] EISO3N %s observations with codes:" % edrop
			print "%s" % sorted(self.dataset[self.dataset.eiso3c.isnull()].eiso3n.unique())
			self.dataset.dropna(subset=['eiso3c'], inplace=True)
		#-Importer-#
		self.dataset = self.dataset.merge(self.country_data[['iso3n', 'iso3c']], how='left', left_on=['iiso3n'], right_on=['iso3n'])
		del self.dataset['iso3n'] 																											#Remove Merge Key
		self.dataset.rename(columns={'iso3c' : 'iiso3c'}, inplace=True)
		if dropna:
			print "[INFO] Removing Units with iiso3c == np.nan"
			idrop = len(self.dataset[self.dataset.iiso3c.isnull()])
			print "[Deleting] IISO3N %s observations with codes:" % idrop
			print "%s" % sorted(self.dataset[self.dataset.iiso3c.isnull()].iiso3n.unique())
			self.dataset.dropna(subset=['iiso3c'], inplace=True)
			self.dataset = self.dataset.reset_index()
			del self.dataset['index']
		if remove_iso3n:
			del self.dataset['eiso3n']
			del self.dataset['iiso3n']
		drop_special, iso3c_list = drop_special
		if drop_special:
			for iso3c in iso3c_list:
				spdrop = len(self.dataset.loc[(self.dataset.iiso3c == iso3c) | (self.dataset.eiso3c == iso3c)])
				if verbose: print "[Deleting] %s country code with %s observations" % (iso3c, spdrop)
				self.dataset.drop(self.dataset.loc[(self.dataset.iiso3c == iso3c) | (self.dataset.eiso3c == iso3c)].index, inplace=True)
		assert init_obs == self.dataset.shape[0]+edrop+idrop+spdrop, "%s != %s" % (init_obs, self.dataset.shape[0])

	def countries_only(self, cid='iso3n', verbose=True):
		"""
		Drop countries specified in country_only_iso3c_deletions, country_only_iso3n_deletions
		Note: this function only uses standard_names (iiso3n, iiso3c etc) 

		Future Work 
		-----------
		[1] Write a decorator to print number of observations before and after the function runs
		"""
		if cid == 'iso3n':
			for item in self.country_only_iso3n_deletions[self.classification]:
				if verbose: print "[INFO] Deleting iiso3n and eiso3n code: %s" % item
				init_numobs = self.dataset.shape[0]
				self.dataset = self.dataset[self.dataset['eiso3n'] != item]
				self.dataset = self.dataset[self.dataset['iiso3n'] != item]
				if verbose: print "[DELETED] %s observations" % (init_numobs - self.dataset.shape[0])
		elif cid == 'iso3c':
			for item in self.country_only_iso3c_deletions[self.classification]:
				if verbose: print "[INFO] Deleting iiso3c and eiso3c code: %s" % item
				init_numobs = self.dataset.shape[0]
				self.dataset = self.dataset[self.dataset['eiso3c'] != item]
				self.dataset = self.dataset[self.dataset['iiso3c'] != item]
				if verbose: print "[DELETED] %s observations" % (init_numobs - self.dataset.shape[0])
		else:
			raise ValueError("'cid' must be 'iso3n' or 'iso3c'")

	def concord_productcode(self, concordance, new_classification, new_level, verbose=True):
		""" 
		Apply a HS6 concordance to convert dataset to a new trade classification
		
		concordance 		: concordance dictionary of HS6 to Something Else
		new_classification

		Future Work 
		-----------
		[1] Account for levels in special cases
		[2] Consider Implimenting Aggregation for quantity
		[3] Automate classification and level encoding

		Note
		----
		[1] Eligible for a Generic Constructor
		"""
		#-Add Special Cases to the concordance-#
		for k,v in  self.adjust_hs6_to_sitc[self.classification].items():
			concordance[k] = v
		self.dataset[new_classification] = self.dataset['hs6'].apply(lambda x: concord_data(concordance, x, issue_error='.'))
		self.dataset = self.dataset[['year', 'eiso3n', 'iiso3n', 'value']+[new_classification]].groupby(['year', 'eiso3n', 'iiso3n']+[new_classification]).sum().reset_index()
		#-Reset Attributes-#
		self.classification = new_classification
		self.level = new_level		


	def merge_all_sourcefiles(self, rename_newvars=True, verbose=True):
		"""
		Merge all baciXX_YYYY.csv, country_code_baciXX.csv, product_code_baciXX.csv files using native column names
		Note
		----
		[1] Is this still useful? => Propose Deletion
		[1] This can be used as a test against using the converted standard_names
		[2] Should I rename incoming data? I think harmonised internal reader friendly columns names are the best solution
		"""
		warnings.warn("[WARNING] This method will reconstruct raw_data and dataset attributes!", UserWarning)
		#-Ensure raw_data is source data-#
		self.load_raw_from_csv(standard_names=False, deletions=False, verbose=verbose)
		self.load_country_data(standard_names=False, verbose=verbose)
		self.load_product_data(fix_source=True, standard_names=False, verbose=verbose)
		#-Merge Datasets-#
		self.dataset = self.raw_data
		#-Countries-#
		#-Exporters-#
		self.dataset = self.dataset.merge(self.country_data[['iso3', 'name_english', 'i']], how="left", left_on='i', right_on=['i'])
		if rename_newvars: 
			self.dataset = self.dataset.rename(columns={'iso3' : 'eiso3c', 'name_english' : 'ename'})
		#-Importers-#
		self.dataset = self.dataset.merge(self.country_data[['iso3', 'name_english', 'i']], how="left", left_on=['j'], right_on=['i'])
		if rename_newvars: 
			self.dataset = self.dataset.rename(columns={'iso3' : 'iiso3c', 'name_english' : 'iname'})
		#-Products-#
		self.dataset = self.dataset.merge(self.product_data[['Code', 'ShortDescription']], how="left", left_on=['hs6'], right_on=['Code'])

	#-----------#
	#-META DATA-#
	#-----------#

	def iso3n_to_countryname_pyfile(self, target_dir='meta/', force=False, verbose=True):
		""" 
		Write Dictionary of iso3n to countryname pyfile from BACI Country Concordance File

		Future Work
		-----------
		[1] Add fix_country_code_baci02
		"""
		if not self.complete_dataset:
			if not force: raise ValueError("This is not a complete dataset!")
		if not self.country_datafl_fixed:
			self.fix_country_code_baci()
		#-Set Filename-#
		fl = '%s_iso3n_to_countryname.py' % (self.classification.lower())
		docstring = "ISO3N to CountryName Dictionary for Classification: %s" % self.classification
		data = pd.read_csv(self.source_dir + self.country_data_fn[self.classification])
		data = data[['i', 'name_english']].set_index('i')
		data = data['name_english']
		data.name = u"iso3n_to_countryname"
		from_idxseries_to_pydict(data, target_dir=target_dir, fl=fl, docstring=docstring, verbose=verbose)

	def iso3n_to_iso3c_pyfile(self, target_dir='meta/', force=False, verbose=True):
		""" 
		Write Dictionary of iso3n to iso3c pyfile from BACI Country Concordance File

		Future Work
		-----------
		[1] Add fix_country_code_baci02
		"""
		if not self.complete_dataset:
			if not force: raise ValueError("This is not a complete dataset!")
		if not self.country_data_fixed:
			self.fix_country_code_baci()
		#-Set Filename-#
		fl = '%s_iso3n_to_iso3c.py' % (self.classification.lower())
		docstring = "ISO3N to CountryName Dictionary for Classification: %s" % self.classification
		docstring += "Source: BACI Country Concordance File"
		data = pd.read_csv(self.source_dir + self.country_data_fn[self.classification])
		data = data[['i', 'iso3']].set_index('i').dropna()
		data = data['iso3']
		data.name = u"iso3n_to_iso3c"
		from_idxseries_to_pydict(data, target_dir=target_dir, fl=fl, docstring=docstring, verbose=verbose)

	#--------------------#
	#-Country Codes Meta-#
	#--------------------#

	def intertemporal_countrycodes(self, cid='iso3c', dataset=False, force=False, verbose=True):
		"""
		Wrapper for Generating intertemporal_countrycodes FROM 'raw_data' or 'dataset'
		"""
		if dataset:
			if verbose: print "Constructing Intertemporal Country Code Tables from Dataset ..."
			table_iiso3n, table_eiso3n = self.intertemporal_countrycodes_dataset(cid=cid, force=force, verbose=verbose)
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

		Interface
		---------
			't' 	: year 
			'hs6' 	: HS 6 Digits
			'i' 	: Exporter
			'j' 	: Importer 
			'v' 	: Value
			'q'	 	: Quantity

		Returns
		-------
			table_iiso3n, table_eiso3n
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Get Raw Data -#
		data = self.raw_data 		
		#-Core-#
		#-Importers-#
		table_iiso3n = data[['t', 'j']]
		table_iiso3n['code'] = table_iiso3n['j'] 					#keep a 'j' in the index
		table_iiso3n = table_iiso3n.drop_duplicates().set_index(['j', 't'])
		table_iiso3n = table_iiso3n.unstack(level='t')
		table_iiso3n.columns = table_iiso3n.columns.droplevel() 	#Removes Unnecessary 'code' label
		#-Exporters-#
		table_eiso3n = data[['t', 'i']]
		table_eiso3n['code'] = table_eiso3n['i'] 					#keep a 'j' in the index
		table_eiso3n = table_eiso3n.drop_duplicates().set_index(['i', 't'])
		table_eiso3n = table_eiso3n.unstack(level='t')
		table_eiso3n.columns = table_eiso3n.columns.droplevel() 	#Removes Unnecessary 'code' label
		return table_iiso3n, table_eiso3n

	def intertemporal_countrycodes_dataset(self, cid='iso3n', force=False, verbose=False):
		"""
		Construct a table of importer and exporter country codes by year from DATASET
		This includes iso3c and is useful when using .countries_only() etc.
		
		force 		:  	True/False
						[Default: True => doesn't raise a ValueError if trying to conduct function on an incomplete dataset]

		Requires standard_names

		Returns
		-------
			table_iiso3, table_eiso3
		"""
		if self.complete_dataset != True:
			if force == False:
				raise ValueError("[ERROR] Not a Complete Dataset!")
		#-Get Dataset-#
		data = self.dataset 
		#-Check Standard Names-#
		if not check_operations(self, u"(use_standard_column_names)"):
			self.use_standard_column_names(data, verbose=verbose) 
		#-Importers-#
		table_iiso3 = data[['year', 'i'+cid]]
		table_iiso3['code'] = table_iiso3['i'+cid] 				#keep a 'j' in the index
		table_iiso3 = table_iiso3.drop_duplicates().set_index(['i'+cid, 'year'])
		table_iiso3 = table_iiso3.unstack(level='year')
		table_iiso3.columns = table_iiso3.columns.droplevel() 	#Removes Unnecessary 'code' label
		#-Exporters-#
		table_eiso3 = data[['year', 'e'+cid]]
		table_eiso3['code'] = table_eiso3['e'+cid] 					#keep a 'j' in the index
		table_eiso3 = table_eiso3.drop_duplicates().set_index(['e'+cid, 'year'])
		table_eiso3 = table_eiso3.unstack(level='year')
		table_eiso3.columns = table_eiso3.columns.droplevel() 	#Removes Unnecessary 'code' label
		return table_iiso3, table_eiso3

	#--------------#
	#---Datasets---#
	#--------------#

	#-Self Contained-#

	def construct_dataset_SC_CP_SITCR2L3_Y1998to2012(self, data_type, dataset_object=True, source_institution='un', verbose=True):
		"""
		Construct a Self Contained (SC) Direct Action Dataset at the Country x Product Level (SITC Level 3)
		Note: SC methods reduce the Need to Debug other routines and methods. 
		The other methods are however useful to diagnose issues and to understand properties of the dataset

		Source Classification: HS96

		data_type 				: 	'trade', 'export', 'import'
								'export' will include values from a country to any region (including NES, and Nuetral Zone etc.)
								'import' will include values to a country from any region (including NES, and Nuetral Zone etc.)

		Note
		----
		[1] NBER Adjustment will happen when joining the two datasets together
		"""

		#-Helper Functions-#
		def merge_iso3c_and_replace_iso3n(data, cntry_data, column):
			" Merge ISO3C and Replace match on column (i.e. eiso3n)"
			data = data.merge(cntry_data, how='left', left_on=[column], right_on=['iso3n'])
			del data['iso3n']
			del data[column]
			data.rename(columns={'iso3c' : column[0:-1]+'c'}, inplace=True)
			return data

		def dropna_iso3c(data, column):
			" Drop iiso3c or eiso3c isnull() values "
			if column == 'iiso3c':
				data.drop(data.loc[(data.iiso3c.isnull())].index, inplace=True)
			elif column == 'eiso3c':
				data.drop(data.loc[(data.eiso3c.isnull())].index, inplace=True)
			return data

		#-Start from RawData-#
		#--------------------#
		data = self.raw_data 
		#-Obtain Key Index Variables-#
		data.rename(columns={'t' : 'year', 'i' : 'eiso3n', 'j' : 'iiso3n', 'v' : 'value', 'q': 'quantity'}, inplace=True) 	#'hs6' is unchanged
		#-Exclude Quantity-#
		del data['quantity']
		#-Import Country Codes to ISO3C-#
		#-------------------------------#
		self.load_country_data(fix_source=True, standard_names=True, verbose=True)	#Using this due to fix required on source files and it's data is attached to self.country_data
		cntry_data = self.country_data[['iso3n', 'iso3c']]
		#-Import Product Concordance-#
		#----------------------------#
		from pyeconlab.trade.concordance import HS2002_To_SITCR2
		concordance = HS2002_To_SITCR2(sitc_level=3).concordance
		#-Add Special Cases to the concordance-#
		for k,v in  self.adjust_hs6_to_sitc[self.classification].items():
			concordance[k] = v
		#-Change Value Units-#
		#--------------------#
		data['value'] = data['value']*1000
		#-Collapse Trade Data based on data option-#
		#------------------------------------------#
		if data_type == "trade":
			#-Merge in ISO3C-#
			#----------------#
			data = merge_iso3c_and_replace_iso3n(data, cntry_data, column='eiso3n')
			data = merge_iso3c_and_replace_iso3n(data, cntry_data, column='iiso3n')
			print "[WARNING] Dropping Countries where iso3c has null() values will remove country export/import from NES, and other regions!"
			data = dropna_iso3c(data, column='eiso3c')
			data = dropna_iso3c(data, column='iiso3c')
			#-Merge in SITCR2 Level 3-#
			#-------------------------#
			data['sitc3'] = data['hs6'].apply(lambda x: concord_data(concordance, x, issue_error=np.nan))
			del data['hs6']
			data = data.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum()
			self.classification = 'SITC' 																		#duplication could be reduced here using a function
			self.revision = 2
			self.level = 3
			print "[Returning] BACI HS96 Source => TRADE data for SITCR2 Level 3 with ISO3C Countries"
		elif data_type == "export" or data_type == "exports":
			#-Export Level-#
			#--------------#
			del data['iiso3n']
			data = data.groupby(['year', 'eiso3n', 'hs6']).sum().reset_index()
			#-Merge in ISO3C-#
			#----------------#
			data = merge_iso3c_and_replace_iso3n(data, cntry_data, column='eiso3n')
			data = dropna_iso3c(data, column='eiso3c')
			#-Merge in SITCR2 Level 3-#
			#-------------------------#
			data['sitc3'] = data['hs6'].apply(lambda x: concord_data(concordance, x, issue_error=np.nan))
			del data['hs6']
			data = data.groupby(['year', 'eiso3c', 'sitc3']).sum()
			self.classification = 'SITC' 																		#duplication could be reduced here using a function
			self.revision = 2
			self.level = 3
			print "[Returning] BACI HS96 Source => EXPORT data for SITCR2 Level 3 with ISO3C Countries"
		elif data_type == "import" or data_type == "imports":
			#-Import Level-#
			#--------------#
			del data['eiso3n']
			data = data.groupby(['year', 'iiso3n', 'hs6']).sum().reset_index()
			#-Merge in ISO3C-#
			#----------------#
			data = merge_iso3c_and_replace_iso3n(data, cntry_data, column='iiso3n')
			data = dropna_iso3c(data, column='iiso3c')
			#-Merge in SITCR2 Level 3-#
			#-------------------------#
			data['sitc3'] = data['hs6'].apply(lambda x: concord_data(concordance, x, issue_error=np.nan))
			del data['hs6']
			data = data.groupby(['year', 'iiso3c', 'sitc3']).sum()
			self.classification = 'SITC' 																		#duplication could be reduced here using a function
			self.revision = 2
			self.level = 3
			print "[Returning] BACI HS96 Source => IMPORT data for SITCR2 Level 3 with ISO3C Countries"
		else:
			raise ValueError("'data' must be 'trade', 'export', or 'import'")
		#-Replace Dataset-#
		self.dataset = data
		self.data_type = data_type
		self.notes = u"HS96L6 to SITCR2L3 => Computed with options: dataset_object=%s, source_institution=%s" % (dataset_object, source_institution)
		#-Return Dataset Object-#
		if dataset_object:
			return self.to_dataset()
	
	def attach_attributes_to_dataset(self, df):
		""" Attach Attributes to the Dataset DataFrame for Transfer """
 		#-Attach Attributes to dataset object for transfer-#
		df.txf_name 			= self.name
		df.txf_data_type 		= self.data_type
		df.txf_classification 	= self.classification
		df.txf_revision 		= self.revision
		df.txf_complete_dataset = self.complete_dataset
		df.txf_notes 			= self.notes
		df.txf_source_revision 	= self.source_revision
		return df

	def to_dataset(self, generic=False):
		""" Convert to a Dataset Object """
		#-Prepare Data for Object Standard Input-#
		data = self.dataset.reset_index()
		data = data.rename_axis({'sitc3' : 'productcode'}, axis=1)
		data = self.attach_attributes_to_dataset(data) 							#Alternatively we could create the object and then attach names directly!
		if self.data_type == "trade":
			if generic:
				return CPTradeData(data)
			return BACITradeData(data)
		elif self.data_type == "export":
			if generic:
				return CPExportData(data)
			return BACIExportData(data)
		elif self.data_type == "import":
			if generic:
				return CPImportData(data)
			return BACIImportData(data)
		else:
			raise ValueError("data_type (%s) is not 'trade', 'export' or 'import'" % self.data_type)	

	#-----------------#
	#---FUTURE WORK---#
	#-----------------#


	def load_raw_from_rar(self, verbose=False):
		""" 
		STATUS: INCOMPLETE - ON HOLD
		Load Raw Data from RAR Files 
		Note
		----
		[1] this will require the installation of unrar!?
		"""
		raise NotImplementedError("Currenlty considering the use of unrar!")
		data = pd.DataFrame()
		for year in self.years:
			fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + str(year) + '.rar'
			print "[INFO] Opening: %s" % fn
			rar = rarfile.RarFile(fn)
			#- Incomplete [currently debating if want to build dependancy on unrar -#