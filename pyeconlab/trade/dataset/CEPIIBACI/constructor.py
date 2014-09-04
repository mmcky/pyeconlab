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
import pandas as pd

from .dataset import BACI

from pyeconlab.util import check_directory

class BACIConstructor(BACI):
	"""
	BACI Data Constructor

	Inheritance
	-----------
		[1] BACI 			: 	Provides Meta Data on CEPII Dataset
		[2] CPTradeDataset	:	Provides CORE Country Product Methods 
	"""

	fn_structure 	= 'baci<classification>_<year>'
	fn_type 		= 'rar' 							#csv?

	def __init__(self, source_dir, src_class, ftype='csv', years=[], std_names=False, skip_setup=False, reduce_memory=False, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 		: 	Must contain the raw csv files
		src_class 		: 	Type of Source Files to Load ['HS92', 'HS96', 'HS02']
		years 			: 	Apply a Year Filter [Default: ALL]
		ftype 			: 	File Type ['rar', 'csv', hdf']
		skip_setup 		: 	[Testing] This allows you to skip __init__ setup of object to manually load the object with csv data etc. 
							This is mainly used for loading test data to check attributes and methods etc. 
		reduce_memory	: 	This will delete self.__raw_data after initializing self._dataset with the raw_data
							[Warning: This will render properties that depend on self.__raw_data inoperable]
							Usage: Useful when building datasets to be more memory efficient as the operations don't require a record of the original raw_data
							[Default: False] Only Saves ~?GB of RAM
		
		"""
		#-Assign Source Directory-#
		self.__source_dir 	= check_directory(source_dir) 	# check_directory() performs basic tests on the specified directory

		#-Set Classification-#
		self.classification = src_class
		if self.classification == "HS02":
			self.product_data_fixed = False 								#Should this be more sophisticated, this is a constructor so probably not

		#-Setup Object-#
		self.std_names = std_names
		if verbose: print "[INFO] Fetching BACI Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True			# This forces object to be imported based on the whole dataset
			years = self.available_years[self.classification] 	
		#-Assign to Attribute-#
		self.years 	= years

		#-Parse Skip Setup-#
		if skip_setup == True:
			print "[INFO] Skipping Setup of BACI Constructor!"
			self.__raw_data 	= None 										#Allows to be assigned later on
			return None

		# - Fetch Raw Data for Years - #
		if ftype == 'rar':
			self.load_raw_from_rar(verbose=verbose)
		elif ftype == 'csv':
			self.load_raw_from_csv(std_names=self.std_names, verbose=verbose)
		elif ftype == 'hdf':
			try:
				self.load_raw_from_hdf(years=years, verbose=verbose)
			except:
				print "[INFO] Your source_directory: %s does not contain h5 version.\nStarting to compile one now ...." % self.source_dir
				# self.load_raw_from_rar(verbose=verbose)
				self.convert_raw_data_to_hdf(verbose=verbose) 			#Compute hdf file for next load
				self.convert_raw_data_to_hdf_yearindex(verbose=verbose)		#Compute Year Index Version Also
		else:
			raise ValueError("ftype must be 'rar', 'csv', or 'hdf'")

		#-Reduce Memory-#
		if reduce_memory:
			self.dataset = self.__raw_data 									#Saves ~2Gb of RAM (but cannot access raw_data)
			self.__raw_data = None
		else:
			self.dataset = self.__raw_data.copy(deep=True) 					#[Default] pandas.DataFrame.copy(deep=True) is much more efficient than copy.deepcopy()

	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years)								+ \
				 "Complete Dataset: %s\n" % (self.complete_dataset) 		+ \
				 "Source Last Checked: %s\n" % (self.source_last_checked)
		return string
	#-Properties-#
	
	@property
	def raw_data(self):
		""" Raw Data Property to Return a Copy of the Private Attribute """ 
		try:
			return self.__raw_data.copy(deep=True)  							#Always Return a Copy
		except: 																#Load from h5 file (quickest Load Times)
			self.load_raw_from_hdf(years=self.years, verbose=False)
			return self.__raw_data.copy(deep=True)

	@property
	def source_dir(self):
		return self.__source_dir

	#-IO-#

	def load_raw_from_csv(self, std_names=True, deletions=True, verbose=False):
		""" 
		Load Raw Data from CSV Files [Main Entry Point for Raw Data]

		std_names : apply standard names [True/False] using interface dictionary
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
			self.__raw_data = self.__raw_data.append(pd.read_csv(fn, dtype={'hs6' : str}))
		self.__raw_data = self.__raw_data.reset_index() 								#Otherwise Each year has repeated obs numbers
		del self.__raw_data['index']
		if deletions:
			for item in self.deletions:
				if verbose: print "[DELETING] Column: %s" % item
				del self.__raw_data[item]
		if std_names:
			self.use_standard_column_names(self.__raw_data)
			
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

	def load_raw_from_hdf(self, years=[], verbose=False):
		"""
		Load HDF Version of RAW Dataset from a source_directory
		Note: 	To construct your own hdf version requires to initially load from BACI supplied RAW dta files
				Then use Constructor method ``convert_source_csv_to_hdf()``

		Questions:
		[1] Should this be moved to Generic Constructor Class?
		"""
		self.__raw_data = pd.DataFrame() 
		if years == []: 						#years assigned prior to loading data
			fn = self.source_dir + self.raw_data_hdf_fn[self.classification]
			if verbose: print "[INFO] Loading RAW DATA from %s" % fn
			self.__raw_data = pd.read_hdf(fn, key='raw_data')
		else:
			fn = self._source_dir + self.raw_data_hdf_yearindex_fn[self.classification] 
			for year in years:
				if verbose: print "[INFO] Loading RAW DATA for year: %s from %s" % (year, fn)
				self.__raw_data = self.__raw_data.append(pd.read_hdf(fn, key='Y'+str(year)))

	def load_country_data(self, verbose=False):
		"""
		Load Country Classification/Concordance File From Archive
		"""
		fn = self.source_dir + self.country_data_fn[self.classification]
		self.country_data = pd.read_csv(fn)
		if self.std_names:
			self.use_standard_column_names(self.country_data)

	def load_product_data(self, fix_source=True, verbose=False):
		"""
		Load Product Code Classification File from Archive
		"""
		if fix_source and self.product_data_fixed == False:
			self.fix_product_code_baci02(verbose=verbose)
		if self.product_data_fixed == False:
			print "[WARNING] Has the product_code_baci02 data been adjusted in the source_dir!"
		fn = self.source_dir + self.product_data_fn[self.classification]
		self.product_data = pd.read_csv(fn, dtype={'Code' : object})
		if self.std_names:
			self.use_standard_column_names(self.product_data)

	def use_standard_column_names(self, df, verbose=True):
		"""
		Use interface attribute to Adjust Columns to use Standard Names (inplace=True)
		"""
		if verbose:
			for item in df.columns:
				try: print "[CHANGING] Column: %s to %s" % (item, self.interface[item])
				except: pass 																#Passing Items not Converted by self.interface
		df.rename(columns=self.interface, inplace=True)


	#-Conversion-#

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
		if self.std_names == True:
			yid = 'year'
		else:
			yid = 't'
		for year in self.raw_data[yearid].unique():
			hdf.put('Y'+str(year), self.raw_data.loc[self.raw_data.year == year], format=format) 	
		if verbose: print hdf
		hdf.close()

	def convert_csv_to_hdf_yearindex(self, years=[], format='fixed', hdf_fn='', verbose=True):
		""" 
		Convert CSV Files to HDF File Indexed by Year
		year 	: 	apply a year filter
		"""
		if years == []:
			years = self.available_years[self.classification]
		#-Setup HDF File-#
		if hdf_fn == '':
			hdf_fn = self.source_dir + self.raw_data_hdf_yearindex_fn[self.classification]
		hdf = pd.HDFStore(hdf_fn, complevel=9, complib='zlib')
		#-Convert Years-#
		for year in years:
			csv_fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + str(year) + '.csv'
			if verbose: print "[INFO] Converting file: %s to file: %s" % (csv_fn, hdf_fn)
			hdf.put('Y'+str(year), pd.read_csv(csv_fn), format=format)
		if verbose: print hdf
		hdf.close()
		return hdf_fn

	#-Fix Source Issues-#

	def fix_product_code_baci02(self, verbose=True):
		"""
		Fix issue with product_code_baci02 csv file
		"""
		if verbose: print "[INFO] Fixing original hs02 product data file in source_dir: %s" % self.source_dir
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
		self.product_data_fixed = True