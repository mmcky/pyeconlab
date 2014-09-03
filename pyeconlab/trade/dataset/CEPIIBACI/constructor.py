"""
Constructor for Working with CEPII/BACI Data

Files
-----
baciHS_YYYY.rar 	where HS=92,96,02 and YYYY=full year

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

import rarfile
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

	def __init__(self, source_dir, stype, ftype='csv', years=[], skip_setup=False, reduce_memory=False, verbose=True):
		""" 
		Load RAW Data into Object

		Arguments
		---------
		source_dir 		: 	Must contain the raw csv files
		stype 			: 	Type of Source Files to Load ['HS92', 'HS96', 'HS02']
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
		self.classification = stype

		#-Parse Skip Setup-#
		if skip_setup == True:
			print "[INFO] Skipping Setup of BACI Constructor!"
			self.__raw_data 	= None 										#Allows to be assigned later on

		#-Setup Object-#
		if verbose: print "[INFO] Fetching BACI Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True	# This forces object to be imported based on the whole dataset
			years = self.available_years 	# Default Years
		#-Assign to Attribute-#
		self.years 	= years

		# - Fetch Raw Data for Years - #
		if ftype == 'rar':
			self.load_raw_from_rar(verbose=verbose)
		elif ftype == 'csv':
			self.load_raw_from_csv(verbose=verbose)
		elif ftype == 'hdf':
			try:
				self.load_raw_from_hdf(years=years, verbose=verbose)
			except:
				print "[INFO] Your source_directory: %s does not contain h5 version.\nStarting to compile one now ...."
				self.load_raw_from_rar(verbose=verbose)
				self.convert_raw_data_to_hdf(verbose=verbose) 			#Compute hdf file for next load
				self.convert_raw_data_to_hdf_yearindex(verbose=verbose)		#Compute Year Index Version Also
		else:
			raise ValueError("ftype must be 'rar', 'csv', or 'hdf'")

		#-Reduce Memory-#
		if reduce_memory:
			self._dataset = self.__raw_data 									#Saves ~2Gb of RAM (but cannot access raw_data)
			self.__raw_data = None
		else:
			self._dataset = self.__raw_data.copy(deep=True) 					#[Default] pandas.DataFrame.copy(deep=True) is much more efficient than copy.deepcopy()

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
		""" Raw Data Property to Return Private Attribute """ 
		try:
			return self.__raw_data.copy(deep=True)  							#Always Return a Copy
		except: 																#Load from h5 file (quickest Load Times)
			self.load_raw_from_hdf(years=self.years, verbose=False)
			return self.__raw_data

	@property
	def source_dir(self):
		return self.__source_dir

	#-IO-#

	def load_raw_from_csv(self, verbose=False):
		""" 
		Load Raw Data from CSV Files

		Questions:
		[1] Should this be moved to Generic Constructor Class? 
		"""
		if verbose: print "[INFO] Loading RAW [.csv] Files from: %s" % (self.source_dir)
		self.__raw_data = pd.DataFrame()
		for year in self.years:
			fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + year + '.csv'
			if verbose: print "[INFO] Loading Year: %s from file: %s" % (year, fn)
			self.__raw_data = self.__raw_data.append(pd.read_csv(fn))
		self.__raw_data = self.__raw_data.reset_index() 								#Otherwise Each year has repeated obs numbers
		del self.__raw_data['index']

	def load_raw_from_rar(self, verbose=False):
		""" 
		Load Raw Data from RAR Files
		Note
		----
		[1] this will require the installation of unrar!?
		"""
		
		raise NotImplementedError()
		
		data = pd.DataFrame()
		for year in self.years:
			fn = self.source_dir + 'baci' + self.classification.strip('HS') + '_' + year + '.rar'
			print "[INFO] Opening: %s" % fn
			rar = rarfile.RarFile(fn)
			#-Incomplete-#

	def load_raw_from_hdf(self, verbose=False):
		"""
		Load HDF Version of RAW Dataset from a source_directory
		Note: 	To construct your own hdf version requires to initially load from BACI supplied RAW dta files
				Then use Constructor method ``convert_source_csv_to_hdf()``

		Questions:
		[1] Should this be moved to Generic Constructor Class?
		"""
		self.__raw_data 	= pd.DataFrame() 
		if years == [] or years == self.available_years: 						#years assigned prior to loading data
			fn = self.source_dir + self.raw_data_hdf_fn
			if verbose: print "[INFO] Loading RAW DATA from %s" % fn
			self.__raw_data = pd.read_hdf(fn, key='raw_data')
		else:
			fn = self._source_dir + self.raw_data_hdf_yearindex_fn 
			for year in years:
				if verbose: print "[INFO] Loading RAW DATA for year: %s from %s" % (year, fn)
				self.__raw_data = self.__raw_data.append(pd.read_hdf(fn, key='Y'+str(year)))