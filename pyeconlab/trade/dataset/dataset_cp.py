"""
Generic Country x Product Dataset Construction Classes

Types
=====
[1] TradeData 	(Bilateral Trade Flows)
[2] ExportData 	(Export Trade Flows)
[3] ImportData 	(Import Trade Flows)

Notes
=====
[1] These objects get inherited by specific datasets. Any child dataset object (i.e. NBERFeenstraWTF) needs to have local class level properties for 
	self.__data, and any other relevant locally stored attributes (self.__exports, self.__imports etc.). This avoids the need to use super etc. when 
	assigning and accessing data

Trade Datasets
==============
1. Feenstra/NBER Data  							[NBERFeenstraWTF]
2. BACI Data 									[CEPIIBACI]

Attribute Datasets
==================
1. UNCTAD Revealed Capital,Labour, and Land 	[TBD]
2. CEPII Datasets 								[TBD]

Issues
======
1. 	How best to Incorporate the Source Dataset files. 
	They can be very large  [Current Strategy: Constructors]
	[Currently will pull in from a MyDatasets Object or manually from a source_dir]

Future Work
===========
[1] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity']
[2] Write a CTradeDataset for Country Level Datasets
[3] Impliment Geographic Aggregates
"""

import pandas as pd
import cPickle as pickle
import warnings
import matplotlib.pyplot as plt

#-Country x Product Trade Dataset-#

class CPTradeDataset(object):
	"""
	Generic Country x Product Trade Data Object ['trade', 'export', 'import']
	This Object Impliments a Standard Interface for Incoming Data allowing methods to be writen easily
	"""

	# - Dataset Attributes - #
	__data 				= pd.DataFrame()		#Holds Data Indexed by Year, Country, Product
	__dyn_data 			= pd.DataFrame() 		#Holds Data Shaped with Years in Columns
	__data_type 		= None 					#'Trade', 'Export', 'Import'
	__level 			= None
	__classification 	= None 					#'HS', 'SICT'
	__revision 			= None  				#'1992', 2
	__name 				= ""
	__years 			= None
	__value_units 		= None
	__value_units_str 	= ""
	__complete_dataset 	= False	
	__interface 		= {
						 'trade' : ['year', 'eiso3c', 'iiso3c', 'productcode', 'value'], 
						 'export' : ['year', 'eiso3c', 'productcode', 'value'],
						 'import' : ['year', 'iiso3c', 'productcode', 'value'],
					  	}
	__notes 			= ""

	#-Source Attributes-#
	source_name 			= None
	source_available_years 	= None
	source_web 				= None
	source_classification 	= None
	source_revision 		= None
	source_level 			= None
	source_value_units 		= None
	source_value_units_str 	= None
	source_last_checked 	= None
	
	#-Internals-#
	__attr_export 	= set(['trade', 'export', 'exports', 'ex'])
	__attr_import	= set(['trade', 'import', 'imports', 'im'])
	 
	def __init__(self, data, data_type, prep_dynamic=True): 	
		""" 
		Fill Object with Data

		Implimented Methods
		-------------------
		[1] from_dataframe
		[2] from_pickle

		Future Work
		-----------
		[1] from_hdf
		"""
		if type(data) == pd.DataFrame:
			self.from_dataframe(data, data_type)
		elif type(data) == str:
			fn, ftype = data.split('.')
			if ftype == 'pickle':
				self.from_pickle(fn=data)
			elif ftype == 'h5':
				self.from_hdf(fn=data)
			else:
				raise ValueError('Uknown File Type: %s' % ftype)

		#-Parse Prepare Dynamic Data Options-#
		if prep_dynamic:
			self.__dyn_data = self.data.unstack(level='year')
			self.__dyn_data.columns = self.dynamic_data.columns.droplevel() 	#remove 'value' label

	def __repr__(self):
		"""
		Future Work: Add in Value Units?
		"""
		try:
			num_exporters = "Number of Exporters: %s\n" % (self.num_exporters)
		except:
			num_exporters = "<Not Applicable>"
		try:
			num_importers = "Number of Importers: %s\n" % (self.num_importers)
		except:
			num_importers = "<Not Applicable>"

		#-Construct REPR-#
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "-------\n" 										 		+ \
				 "DATASET:\n" 										 		+ \
				 "Name: %s (Type: %s)\n" % (self.__name, self.__data_type) 		+ \
				 "Classification: %s (L:%s) [R:%s]\n" % (self.__classification, self.__level, self.__revision) + \
				 num_exporters 												+ \
				 num_importers 												+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Trade Flows: %s\n" % (self.data.shape[0])   	+ \
				 "Years: %s\n" % (self.__years)								+ \
				 "Complete Dataset: %s\n" % (self.__complete_dataset) 		+ \
				 "Dataset Notes: %s\n" % (self.__notes) 					+ \
				 "-------\n" 										 		+ \
				 "SOURCE:\n"	 											+ \
				 "%s (%s)\n" % (self.source_name, self.source_web) 			+ \
				 "Last Checked: %s" % (self.source_last_checked)
		return string.replace("<Not Applicable>", "")

	#-Class Properties-#
	@classmethod
	def load_pickle(cls, fn):
		fl = open(fn, 'rb')
		cls = pickle.load(fl)
		fl.close()
		return cls

	#-Properties-#

	@property 
	def data(self):
		return self.__data

	@property 
	def dynamic_data(self):
		return self.__dyn_data

	@property 
	def years(self):
		return self.__years
	@years.setter
	def years(self, value):
		self.__years = value

	@property 
	def num_years(self):
		""" Number of Years """
		loc = self.data.index.names.index('year')
		return self.data.index.levshape[loc]

	@property 
	def num_products(self):
		""" Number of Products """
		loc = self.data.index.names.index('productcode')
		return self.data.index.levshape[loc]

	@property 
	def classification(self):
		return self.__classification

	@property 
	def revision(self):
		return self.__revision

	@property
	def sitc_level(self):
		return self.__level

	@property 
	def interface(self):
		return self.__interface

	@property 
	def complete_dataset(self):
		return self.__complete_dataset

	#-Data Extraction-#

	@property 
	def exporters(self):
		""" List of Exporters """
		if self.data_type in self.__attr_export:
			return self.data.index.get_level_values(level='eiso3c').unique()
		else:
			raise ValueError("%s is data that does not contain exporter characteristics" % self.data_type)

	@property 
	def importers(self):
		""" List of Importers """
		if self.data_type in self.__attr_import:
			return self.data.index.get_level_values(level='iiso3c').unique()
		else:
			raise ValueError("%s is data that does not contain exporter characteristics" % self.data_type)

	#-IO-#

	def from_dataframe(self, df, data_type):
		"""
		Populate Object from Pandas DataFrame
		
		Notes
		-----
		[1] Bring Attributes in as df.attribute
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface[data_type.lower()]:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.__name = df.txf_name
			self.__data_type = data_type
			self.__classification = df.txf_classification 
			self.__revision = df.txf_revision
				# self.__value_units = df.txf_value_units 						#Add in Later
			self.__complete_dataset = df.txf_complete_dataset
			self.__notes = df.txf_notes
			#-Infer Years-#
			self.__years = list(df['year'].unique())
			#-Infer Level-#
			levels = df['productcode'].apply(lambda x: len(x)).unique()
			if len(levels) > 1:
				raise ValueError("Product Levels are not consistent lengths: %s" % levels)
			self.__level = levels[0]
			#-Set Index-#
			self.data = df.set_index(self.interface[data_type.lower()][:-1]) 	#Index by all values except 'value'
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface[data_type.lower()])

	def to_pickle(self, fn):
		""" 
		Pickle Object
		Notes
		-----
		This can be restored from:
			[1] the pickle file 			
								import cPickle
								fl = open(<fl>, 'rb')
								obj = cPickle.load(filename)
								fl.close()
			[2] the class method
								import pyeconlab as ec
								ec.BACIExportData.load_pickle(fn=<filename>)
			[3] the from_pickle method
						 		import pyeconlab as ec
								ec.BACIExportData(data=<pickle filename>)
		"""
		fl = open(fn, 'wb')	
		pickle.dump(self, fl, 2)
		fl.close()

	def from_pickle(self, fn):
		""" 
		Load Object from Pickle
		Notes
		-----
		[1] Load Object from Pickle and assign current object with data.
		"""
		fl = open(fn, 'rb')
		obj = pickle.load(fl)
		fl.close()
		self.__dict__.update(obj.__dict__)

	def to_hdf(self, fn):
		"""
		Populate Object from HDF File
		"""
		raise NotImplementedError

	def from_hdf(self, fn):
		"""
		Populate Object from HDF File
		"""
		raise NotImplementedError

	#-Methods-#

	def check_interface(self, columns, data_type):
		""" Checking Incoming Data Conforms to Interface """
		columns = set(columns)
		for item in self.interface[data_type.lower()]:
			if item not in columns: 
				raise TypeError("Need %s to be specified in the incoming data" % item)

	#-Country / Aggregates Filters-#

	def geo_aggregates(self, members):
		"""
		Geographic Aggregates

		Note: Given this methods location, it will have to try eiso3c and iiso3c as this is inherited by both Trade, Import and Export Datasets

		members = dict {'iso3c' : 'region'}
		Subsitute Country Names for Regions and Collapse.sum()
		"""
		raise NotImplementedError


	#-Plots-#
	def plot_cp_value(self, c, p):
		""" Plot Country, Product Time Series """
		plot = self.dynamic_data.ix[(c,p)].plot(title="Country: %s; Product: %s" % (c,p))
		return plot


#-Specific Trade Data Object-#

class CPTradeData(CPTradeDataset):
	""" 
	Country x Product bilateral TRADE Dataset Object
	Interface: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']
	Future Work:
	-----------
	[1] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity'], 
	"""

	__data_type = 'Trade'

	def __init__(self, data):
		""" Use Superclass init() with specified data_type """
		CPTradeDataset.__init__(self, data, self.__data_type)

	#-Properties-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	@property 
	def exports(self):
		try:
			return self.__exports
		except:
			self.export_data()
			return self.__exports
	@exports.setter
	def exports(self, values):
		self.__exports = values

	@property 
	def imports(self):
		try:
			return self.__imports
		except:
			self.import_data()
			return self.__imports
	@imports.setter
	def imports(self, values):
		self.__imports = values

	@property 
	def num_exporters(self):
		""" Number of Exporters """
		try:
			loc = self.data.index.names.index('eiso3c')
		except:
			warnings.warn("'eiso3c' is not found in the data", UserWarning)
		return self.data.index.levshape[loc]

	@property 
	def num_importers(self):
		""" Number of Importers """
		try:
			loc = self.data.index.names.index('iiso3c')
		except:
			warnings.warn("'iiso3c' is not found in the data", UserWarning)
		return self.data.index.levshape[loc]

	#-Exports / Imports Data-#

	def export_data(self, return_data=False):
		"""
		Collapse to obtain Export Data
		"""
		warnings.warn("This method aggregates across iiso3c for every eiso3c. This most likely will not include NES regions if they have been discarded in the constructor (as they do not belong to any given importer)", UserWarning)
		self.exports = self.data.reset_index()[['year', 'eiso3c', 'productcode', 'value']].groupby(['year', 'eiso3c', 'productcode']).sum()
		if return_data:
			return self.exports

	def import_data(self, return_data=False):
		"""
		Collapse to obtain Import Data
		"""
		warnings.warn("This method aggregates across iiso3c for every eiso3c. This most likely will not include NES regions if they have been discarded in the constructor (as they do not belong to any given importer)", UserWarning)
		self.imports = self.data.reset_index()[['year', 'iiso3c', 'productcode', 'value']].groupby(['year', 'iiso3c', 'productcode']).sum()
		if return_data:
			return self.imports

#-Export Data-#

class CPExportData(CPTradeDataset):
	""" 
	Country x Product EXPORT Dataset Object
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""

	__data = pd.DataFrame()
	__data_type = 'Export'

	def __init__(self, data):
		""" Use Superclass init() with specified data_type """
		CPTradeDataset.__init__(self, data, self.__data_type)

	#-Properties-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	@property 
	def exports(self):
		return self.__data

	@property 
	def num_exporters(self):
		""" Number of Exporters """
		try:
			loc = self.data.index.names.index('eiso3c')
		except:
			warnings.warn("'eiso3c' is not found in the data", UserWarning)
		return self.data.index.levshape[loc]

	def to_dynamic_productlevelexportsystem(self, verbose=True):
		"""
		Method to construct a Product Level Export System from the dataset
		Note: This requires 'export' data
		"""
		#-Prepare Names-#
		data = self.data.copy(deep=True) 											#Don't Alter Dataset, Should this be the default behaviour of the data attribute?
		data = data.reset_index()
		data.rename(columns={'eiso3c' : 'country', 'value' : 'export'}, inplace=True)
		data.set_index(['year'], inplace=True)
		#-Construct Object-#
		from pyeconlab.trade.systems import DynamicProductLevelExportSystem
		system = DynamicProductLevelExportSystem()
		system.from_df(df=data)
		return system


#-Import Data-#

class CPImportData(CPTradeDataset):
	""" 
	Country x Product IMPORT Dataset Object
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	
	__data = pd.DataFrame()
	__data_type = 'Import'

	def __init__(self, data):
		""" Use Superclass init() with specified data_type """
		CPTradeDataset.__init__(self, data, self.__data_type)

	#-Properties-#
	
	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	@property 
	def imports(self):
		return self.__data

	@property 
	def num_importers(self):
		""" Number of Importers """
		try:
			loc = self.data.index.names.index('iiso3c')
		except:
			warnings.warn("'iiso3c' is not found in the data", UserWarning)
		return self.data.index.levshape[loc]

