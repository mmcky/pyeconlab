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
import pandas as pd

from .dataset import BACI

from pyeconlab.util import check_directory, check_operations, update_operations, from_idxseries_to_pydict

class BACIConstructor(BACI):
	"""
	BACI Data Constructor

	Inheritance
	-----------
		[1] BACI 			: 	Provides Meta Data on CEPII Dataset
		[2] CPTradeDataset	:	Provides CORE Country Product Methods 

	Notes
	-----
	[1] When should standard_names be implimented (at the beginning or at the end?)
		Beginning: update all native imports, but a bit easier to read in the programming
		End: all baci files merge natively untouched. Could write a merge routine to undertake this approach as a check against using standard_names

	Questions
	---------
	[1] Should self.raw_data have i,j etc rather than standard_names if it is to be untouched.
	"""

	fn_structure 	= 'baci<classification>_<year>'
	fn_type 		= 'rar' 							#csv?
	#-Defaults-#
	std_names 		= False

	def __init__(self, source_dir, src_class, ftype='csv', years=[], std_names=True, skip_setup=False, reduce_memory=False, verbose=True):
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
		
		Future Work
		-----------
		[1] Should I add a hdf_fn='' option for specifying a h5 file rather than using the internal defaults?
		"""
		#-Assign Source Directory-#
		self.__source_dir 	= check_directory(source_dir) 	# check_directory() performs basic tests on the specified directory

		#-Set Classification-#
		self.classification = src_class
		if self.classification == "HS02":
			self.product_data_fixed = False 								#Should this be more sophisticated, this is a constructor so probably not
			self.country_data_fixed = False

		#-Setup Object-#
		if verbose: print "[INFO] Fetching BACI Data from %s" % source_dir
		if years == []:
			self.complete_dataset = True			# This forces object to be imported based on the whole dataset
			years = self.available_years[self.classification] 	
		#-Assign to Attribute-#
		self.years 	= years
		#-Dataset Operations-#
		self.operations = ""

		#-Parse Skip Setup-#
		if skip_setup == True:
			print "[INFO] Skipping Setup of BACI Constructor!"
			self.__raw_data 	= None 										#Allows to be assigned later on
			return None

		# - Fetch Raw Data for Years - #
		if ftype == 'rar':
			self.load_raw_from_rar(verbose=verbose)
		elif ftype == 'csv':
			self.load_raw_from_csv(std_names=False, verbose=verbose)
		elif ftype == 'hdf':
			try:
				self.load_raw_from_hdf(years=years, verbose=verbose)
			except:
				print "[INFO] Your source directory: %s does not contain h5 version.\nStarting to compile one now ...." % self.source_dir
				self.load_raw_from_csv(std_names=False, verbose=verbose)
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
		self.std_names = std_names
		if self.std_names:
			self.use_standard_column_names(self.dataset, verbose=verbose)


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

	def load_raw_from_csv(self, std_names=False, deletions=True, verbose=False):
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
			for item in self.deletions[self.classification]:
				if verbose: print "[DELETING] Column: %s" % item
				del self.__raw_data[item]
		if std_names:
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
		if years == [] or years == self.available_years[self.classification]:
			fn = self.source_dir + self.raw_data_hdf_fn[self.classification]
			if verbose: print "[INFO] Loading RAW DATA from %s" % fn
			self.__raw_data = pd.read_hdf(fn, key='raw_data')
		else:
			fn = self.source_dir + self.raw_data_hdf_yearindex_fn[self.classification] 
			for year in years:
				if verbose: print "[INFO] Loading RAW DATA for year: %s from %s" % (year, fn)
				self.__raw_data = self.__raw_data.append(pd.read_hdf(fn, key='Y'+str(year)))

	def load_country_data(self, fix_source=True, std_names=True, verbose=False):
		"""
		Load Country Classification/Concordance File From Archive
		"""
		if fix_source and self.country_data_fixed == False:
			self.fix_country_code_baci02(verbose=verbose)
		if self.country_data_fixed == False:
			print "[WARNING] Has the country_code_baci02 data been adjusted in the source_dir!"
		fn = self.source_dir + self.country_data_fn[self.classification]
		self.country_data = pd.read_csv(fn)
		if std_names:
			self.country_data.rename(columns={'i' : 'iso3n', 'iso3' : 'iso3c'}, inplace=True)

	def load_product_data(self, fix_source=True, std_names=True, verbose=False):
		"""
		Load Product Code Classification File from Archive
		"""
		if fix_source and self.product_data_fixed == False:
			self.fix_product_code_baci02(verbose=verbose)
		if self.product_data_fixed == False:
			print "[WARNING] Has the product_code_baci02 data been adjusted in the source_dir!"
		fn = self.source_dir + self.product_data_fn[self.classification]
		self.product_data = pd.read_csv(fn, dtype={'Code' : object})
		if std_names:
			self.use_standard_column_names(self.product_data)

	def use_standard_column_names(self, df, verbose=True):
		"""
		Use interface attribute to Adjust Columns to use Standard Names (inplace=True)
		"""
		opstring = u"(use_standard_column_names)"
		if verbose:
			for item in df.columns:
				try: print "[CHANGING] Column: %s to %s" % (item, self.interface[item])
				except: pass 																#Passing Items not Converted by self.interface
		df.rename(columns=self.interface, inplace=True)
		#-Update Operations Attribute-#
		update_operations(self, opstring)


	#-Conversion-#

	def convert_raw_data_to_hdf(self, key='raw_data', format='table', hdf_fn='', verbose=True):
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
	
	def convert_raw_data_to_hdf_yearindex(self, format='table', hdf_fn='', verbose=True):
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
		for year in self.raw_data[yid].unique():
			hdf.put('Y'+str(year), self.raw_data.loc[self.raw_data[yid] == year], format=format) 	
		if verbose: print hdf
		hdf.close()

	def convert_csv_to_hdf_yearindex(self, years=[], format='table', hdf_fn='', verbose=True):
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
		self.country_data_fixed = True

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

	#-Datasets-#
	
	def add_country_iso3c(self, remove_iso3n=False, dropna=True, verbose=True):
		"""
		Add CountryNames to ISO3N Codes
		"""
		edrop, idrop = 0,0
		init_obs = self.dataset.shape[0]
		#-Exporter-#
		self.dataset = self.dataset.merge(self.country_data[['iso3n', 'iso3c']], how='left', left_on=['eiso3n'], right_on=['iso3n'])
		del self.dataset['iso3n'] 																											#Remove Merge Key
		self.dataset.rename(columns={'iso3c' : 'eiso3c'}, inplace=True)
		if dropna:
			print "[INFO] Removing Units with eiso3c == np.nan"
			edrop = len(self.dataset[self.dataset.eiso3c.isnull()])
			print "[Deleting] EISO3N %s observations with codes:" % edrop
			print "%s" % self.dataset[self.dataset.eiso3c.isnull()].eiso3n.unique()
			self.dataset.dropna(subset=['eiso3c'], inplace=True)
		#-Importer-#
		self.dataset = self.dataset.merge(self.country_data[['iso3n', 'iso3c']], how='left', left_on=['iiso3n'], right_on=['iso3n'])
		del self.dataset['iso3n'] 																											#Remove Merge Key
		self.dataset.rename(columns={'iso3c' : 'iiso3c'}, inplace=True)
		if dropna:
			print "[INFO] Removing Units with iiso3c == np.nan"
			idrop = len(self.dataset[self.dataset.iiso3c.isnull()])
			print "[Deleting] IISO3N %s observations with codes:" % idrop
			print "%s" % self.dataset[self.dataset.iiso3c.isnull()].iiso3n.unique()
			self.dataset.dropna(subset=['iiso3c'], inplace=True)
			self.dataset = self.dataset.reset_index()
			del self.dataset['index']
		if remove_iso3n:
			del self.dataset['eiso3n']
			del self.dataset['iiso3n']
		assert init_obs == self.dataset.shape[0]+edrop+idrop, "%s != %s" % (init_obs, self.dataset.shape[0])

	def merge_all_sourcefiles(self, rename_newvars=True, verbose=True):
		"""
		Merge all baciXX_YYYY.csv, country_code_baciXX.csv, product_code_baciXX.csv files using native column names
		
		Note
		----
		[1] This can be used as a test against using the converted standard_names
		[2] Should I rename incoming data? I think harmonised internal reader friendly columns names are the best solution
		"""
		warnings.warn("[WARNING] This method will reconstruct raw_data and dataset attributes!", UserWarning)
		#-Ensure raw_data is source data-#
		self.load_raw_from_csv(std_names=False, deletions=False, verbose=verbose)
		self.load_country_data(std_names=False, verbose=verbose)
		self.load_product_data(fix_source=True, std_names=False, verbose=verbose)
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

	def iso3n_to_countryname_pyfile(self, target_dir='meta', verbose=True):
		""" 
		Write Dictionary of iso3n to countryname pyfile

		Future Work
		-----------
		[1] Add fix_country_code_baci02
		"""
		#-Set Filename-#
		fl = '%s_baci_iso3n_to_countryname.py' % (self.classification.lower())
		docstring = "ISO3N to CountryName Dictionary for Classification: %s" % self.classification
		data = pd.read_csv(self.source_dir + self.country_data_fn[self.classification])
		data = data[['i', 'name_english']].set_index('i')
		from_idxseries_to_pydict(data['name_english'], target_dir=target_dir, fl=fl, docstring=docstring, verbose=verbose)


	# - Country Codes Meta - #

	def intertemporal_countrycodes(self, cid='iso3c', dataset=False, force=False, verbose=True):
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


	#---FUTURE WORK-----#


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