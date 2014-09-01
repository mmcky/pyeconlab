"""
NBERFeenstraWTF Dataset Object

Supporting Constructor: NBERFeenstraConstructor

Types
=====
[1] Trade Dataset (Bilateral Trade Flows)
[2] Export Dataset (Export Trade Flows)
[3] Import Dataset (Import Trade Flows)

Future Work
-----------
[1] Can properties and attributes be generalised to the BASE Class NBERFeenstraWTF?

"""

import pandas as pd

class NBERFeenstraWTF(object):
	"""
	Parent Class for Trade, Export and Import Objects
	
	Source Dataset Attributes
	-------------------------
	Years: 			1962 to 2000
	Classification: SITC R2 L4
	Notes: 			Pre-1974 care is required for constructing intertemporally consistent data

	"""

	# - Attributes - #
	name 			= u'Feenstra (NBER) World Trade Dataset'
	years 			= []
	available_years = xrange(1962, 2000, 1)
	classification 	= 'SITC'
	revision 		= 2
	level 			= 4
	source_web 		= u"http://cid.econ.ucdavis.edu/nberus.html"
	raw_units 		= 1000
	raw_units_str 	= u'US$1000\'s'
	interface 		= {
						 'trade' : ['year', 'eiso3c', 'iiso3c', 'productcode', 'value'], 
						 'export' : ['year', 'eiso3c', 'productcode', 'value'],
						 'import' : ['year', 'iis3oc', 'productcode', 'value'],
					  }

#-------#
#-Trade-#
#-------#

class NBERFeenstraWTFTrade(NBERFeenstraWTF):
	"""
	Feenstra NBER Bilateral World TRADE Data
	
	Interfaces: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']

	Future Work:
	-----------
	[1] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity'], 
	"""

	data = None

	def __init__(self, data, years=[]): 	
		""" 
		Fill Object with Data

		Implimented Methods
		-------------------
		[1] from_dataframe(**kwargs)

		Future Work
		-----------
		[1] from_pickle
		[2] from_hd5py
		"""
		if years == []:
			years = list(self.data['year'].unique())
		self.from_dataframe(data, years)
		
	
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
		return self.data

	@property 
	def num_years(self):
		""" Number of Years """
		loc = self.data.index.names('year')
		return self.data.index.levshape[loc]

	@property 
	def num_exporters(self):
		""" Number of Exporters """
		loc = self.data.index.names('eiso3c')
		return self.data.index.levshape[loc]

	@property 
	def num_importers(self):
		""" Number of Importers """
		loc = self.data.index.names('iiso3c')
		return self.data.index.levshape[loc]

	@property 
	def num_products(self):
		""" Number of Products """
		loc = self.data.index.names('productcode')
		return self.data.index.levshape[loc]
	
	#-Data Import Methods-#

	def from_dataframe(self, df, years):
		"""
		Populate Object from Pandas DataFrame
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface['trade']:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.data = df.set_index(self.interface['trade'][:-1]) 	#Index by all values except 'value'
			self.years = years
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface['trade'])
		return self

	def from_pickle(self, fl):
		"""
		Populate Object from Pickle File 
		"""
		raise NotImplementedError

	def from_hdf(self, fl):
		"""
		Populate Object from hd5py File
		"""
		raise NotImplementedError

	#-Country / Aggregates Filters-#

	def country_data(self):
		pass

	def world_data(self):
		pass

	def geo_aggregates(self, members):
		"""
		members = dict {'iso3c' : 'region'}
		Subsitute Country Names for Regions and Collapse.sum()
		"""
		pass 

	#-Exports / Imports Data-#

	def export_data(self):
		"""
		Extract Export Data from Raw Data and Return NBERFeenstraWTFExport
		"""
		from pyeconlab.trade.concordance import NBERFeenstraExportersToISO3C, concord_data
		
		expdata = self.data[['year', 'exporter', 'sitc4', 'value']]
		cntrynotfound = []
		expdata['exporter'] = expdata['exporter'].apply(lambda x: concord_data(NBERFeenstraExportersToISO3C, x))

		### --- Working Here --- #

		self.exports = expdata
		return self.exports

	def import_data(self):
		"""
		Extract Import Data from Data and Return NBERFeenstraWTFImport
		"""
		pass

#--------#
#-Export-#
#--------#

class NBERFeenstraWTFExport(NBERFeenstraWTF):
	"""
	NBER Feenstra EXPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""

	def __init__(self, data, years=[]): 	
		""" 
		Fill Object with Data

		Implimented Methods
		-------------------
		[1] from_dataframe(**kwargs)

		Future Work
		-----------
		[1] from_pickle
		[2] from_hd5py
		"""
		if years == []:
			years = list(self.data['year'].unique())
		self.from_dataframe(data, years)
		
	
	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" % (self.available_years)		+ \
				 "Number of Exporters: %s\n" % (self.num_exporters)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Export Flows: %s\n" % (self.data.shape[0])
		return string


	#-Data Import Methods-#

	def from_dataframe(self, df, years):
		"""
		Populate Object from Pandas DataFrame
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface['export']:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.__data = df.set_index(self.interface['export'][:-1]) 	#Index by all values except 'value'
			self.years = years
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface['export'])
		return self


	#-Country / Aggregates Filters-#

	def geo_aggregates(self, members):
		"""
		members = dict {'iso3c' : 'region'}
		Subsitute Country Names for Regions and Collapse.sum()
		"""
		pass 

	
#--------#
#-Import-#
#--------#

class NBERFeenstraWTFImport(NBERFeenstraWTF):
	"""
	NBER Feenstra IMPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""
	def __init__(self, data, years=[]): 	
		""" 
		Fill Object with Data

		Implimented Methods
		-------------------
		[1] from_dataframe(**kwargs)

		Future Work
		-----------
		[1] from_pickle
		[2] from_hd5py
		"""
		if years == []:
			years = list(self.data['year'].unique())
		self.from_dataframe(data, years)
		
	
	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" % (self.available_years)		+ \
				 "Number of Exporters: %s\n" % (self.num_exporters)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Export Flows: %s\n" % (self.data.shape[0])
		return string


	#-Data Import Methods-#

	def from_dataframe(self, df, years):
		"""
		Populate Object from Pandas DataFrame
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface['import']:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.__data = df.set_index(self.interface['import'][:-1]) 	#Index by all values except 'value'
			self.years = years
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface['import'])
		return self
