"""
Dataset Construction Classes

Datasets:
--------
1. Feenstra/NBER Data 
2. BACI Data
3. CEPII Data
4. UNCTAD Revealed Capital,Labour, and Land

Issues:
-------
1. 	How best to Incorporate the Source Dataset files. They can be very large  [Current Strategy: Constructors]
	[Currently will pull in from a MyDatasets Object]
"""

import pandas as pd
import cPickle as pickle

class TradeDataset(object):
	"""
	Generic Trade Data Object
	This Object Impliments a Standard Interface for Incoming Data allowing methods to be writen easily
	"""

	# - Attributes - #
	name 			= None
	years 			= None
	available_years = None
	classification 	= None
	revision 		= None 
	level 			= None
	source_web 		= None
	raw_units 		= None
	raw_units_str 	= None
	interface 		= {
						 'trade' : ['year', 'eiso3c', 'iiso3c', 'productcode', 'value'], 
						 'export' : ['year', 'eiso3c', 'productcode', 'value'],
						 'import' : ['year', 'iiso3c', 'productcode', 'value'],
					  }

	def __init__(self, data): 	
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
			self.from_dataframe(data)
		elif type(data) == str:
			fn, ftype = data.split('.')
			if ftype == 'pickle':
				self.from_pickle(fn=data)
			elif ftype == 'h5':
				self.from_hdf(fn=data)
			else:
				raise ValueError('Uknown File Type: %s' % ftype)

	@property 
	def num_years(self):
		""" Number of Years """
		loc = self.data.index.names.index('year')
		return self.data.index.levshape[loc]

	@property 
	def num_exporters(self):
		""" Number of Exporters """
		loc = self.data.index.names.index('eiso3c')
		return self.data.index.levshape[loc]

	@property 
	def num_importers(self):
		""" Number of Importers """
		loc = self.data.index.names.index('iiso3c')
		return self.data.index.levshape[loc]

	@property 
	def num_products(self):
		""" Number of Products """
		loc = self.data.index.names.index('productcode')
		return self.data.index.levshape[loc]

	@property
	def sitc_level(self):
		return self.level

	#-IO-#

	def load_dataframe(self, df, dtype):
		"""
		Populate Object from Pandas DataFrame
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface[dtype]:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.data = df.set_index(self.interface[dtype][:-1]) 	#Index by all values except 'value'
			#-Infer Years-#
			self.years = list(df['year'].unique())
			#-Infer Level-#
			levels = df['productcode'].apply(lambda x: len(x)).unique()
			if len(levels) > 1:
				raise ValueError("Product Levels are not consistent lengths: %s" % levels)
			self.level = levels[0]
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface[dtype])

	def to_pickle(self, fn):
		""" Pickle Object """
		with open(fn, 'w') as f:
			pickle.dump(self, f)
		f.close()

	def from_pickle(self, fn):
		""" 
		Load Object from Pickle
		Notes
		-----
		[1] Load Object from Pickle and assign current object with data. All non-derived items should be transfered.  
		"""
		fl = open(fn, 'r')
		obj = pickle.load(fl)
		if type(obj) != self.__class__:
			raise ValueError("Pickle Object doesn't contain a %s object!\nIt's type is: %s" % (str(self.__class__).split('.')[-1].split("'")[0], str(obj.__class__).split('.')[-1].split("'")[0]))
		#-Populate Object-#
		self.data = obj.data
		self.years = obj.years
		self.level = obj.level

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

	def check_interface(self, columns, dtype):
		""" Checking Incoming Data Conforms to Interface """
		columns = set(columns)
		for item in self.interface[dtype]:
			if item not in columns: 
				raise TypeError("Need %s to be specified in the incoming data" % item)

	#-Country / Aggregates Filters-#

	def geo_aggregates(self, members):
		"""
		members = dict {'iso3c' : 'region'}
		Subsitute Country Names for Regions and Collapse.sum()
		"""
		pass

#-InWork-#

class TradeData(TradeDataset):
	""" 
	Generic Trade Dataset Object
	
	Interface: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']

	Future Work:
	-----------
	[1] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity'], 
	"""

	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" 	% (self.available_years)		+ \
				 "Number of Importers: %s\n" % (self.num_importers) 		+ \
				 "Number of Exporters: %s\n" % (self.num_exporters)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Trade Flows: %s\n" % (self.data.shape[0])
		return string

	#-Properties-#
	
	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	@property 
	def exports(self):
		return self.__exports
	@exports.setter
	def exports(self, values):
		self.exports = values

	@property 
	def imports(self):
		return self.__imports
	@imports.setter
	def imports(self, values):
		self.imports = values

	#-Data Import Methods-#

	def from_dataframe(self, df):
		self.load_dataframe(df, dtype='trade')

	#-Exports / Imports Data-#

	def export_data(self):
		"""
		Collapse to obtain Export Data
		"""
		print "[WARNING] This method aggregates across iiso3c for every eiso3c. This most likely will not include NES regions if they have been discarded in the constructor (as they do not belong to any given importer)"
		self.exports = self.reset_index().data[['year', 'eiso3c', 'sitc%s'%self.level, 'value']].groupby(['year', 'eiso3c', 'sitc%s'%self.level]).sum()
		return self.exports

	def import_data(self):
		"""
		Collapse to obtain Import Data
		"""
		print "[WARNING] This method aggregates across eiso3c for every iiso3c. This most likely will not include NES regions if they have been discarded in the constructor (as they do not belong to any given exporter)"
		self.imports = self.reset_index().data[['year', 'iiso3c', 'sitc%s'%self.level, 'value']].groupby(['year', 'iiso3c', 'sitc%s'%self.level]).sum()
		return self.imports

class ExportData(TradeDataset):
	""" 
	Generic Export Dataset Object

	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""
	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" % (self.available_years)		+ \
				 "Number of Exporters: %s\n" % (self.num_exporters)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Export Flows: %s\n" % (self.data.shape[0])
		return string

	#-Data Import Methods-#

	def from_dataframe(self, df):
		self.load_dataframe(df, dtype='export')

	#-Properties-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

class ImportData(TradeDataset):
	""" 
	Generic Import Dataset Object
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	
	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" % (self.available_years)		+ \
				 "Number of Importers: %s\n" % (self.num_importers)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Import Flows: %s\n" % (self.data.shape[0])
		return string

	#-Properties-#
	
	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	#-Data Import Methods-#

	def from_dataframe(self, df):
		self.load_dataframe(df, dtype='import')
