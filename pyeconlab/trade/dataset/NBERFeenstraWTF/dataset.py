"""
NBERFeenstraWTF Dataset Object

Supporting Constructor: NBERFeenstraConstructor
"""

import pandas as pd

#from .constructor import NBERFeenstraWTFConstructor

class NBERFeenstraWTF(object):
	"""
	Data Object for Feenstra NBER World Trade Data
	
	Attributes:
	-----------
	Years: 			1962 to 2000
	Classification: SITC R2 L4
	Notes: 			Pre-1974 care is required for constructing intertemporally consistent data

	Current Interfaces
	------------------ 
	['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value']

	Notes
	-----
	[1] Attributes are repeated here as the NBERFeenstraWTFConstructor may not be the only entry point

	Future Work:
	-----------
	[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
	[2] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity'], 

	"""

	# - Attributes - #
	name 			= 'Feenstra (NBER) World Trade Dataset'
	years 			= []
	available_years = xrange(1962, 2000, 1)
	classification 	= 'SITC'
	revision 		= 2
	level 			= 4
	source_web 		= u"http://cid.econ.ucdavis.edu/nberus.html"
	raw_units 		= 1000
	raw_units_str 	= u'US$1000\'s'
	interface 		= {
						 'default' : ['year', 'eiso3c', 'iiso3c', 'productcode', 'value'], 
					  }

	# - Internal Methods - #

	def __init__(self): 	
		""" 
		Set Core Attributes of the Dataset
		
		To populate the object with data use:
			[1] from_dataframe(**kwargs)
			[2] from_constructor(**kwargs)

		Future Work
		-----------
		[1] from_pickle
		[2] from_hd5py
		"""
		self.__data = None
	
	def __repr__(self):
		""" Representation String Of Object """
		string = "Class: %s\n" % (self.__class__) 							+ \
				 "Years: %s\n" % (self.years) +  " [Available Years: %s]\n" 	% (self.available_years)		+ \
				 "Number of Importers: %s\n" % (self.num_importers) 		+ \
				 "Number of Exporters: %s\n" % (self.num_exporters)			+ \
				 "Number of Products: %s\n" % (self.num_products) 			+ \
				 "Number of Trade Flows: %s\n" % (self.data.shape[0])
		return string

	# -------------- #
	# - Properties - #
	# -------------- #

	@property 
	def data(self):
		try:
			if self.__data == None:
				print "[ERROR] Object Needs to be populated with data with the from_ methods"
		except:
			return self.__data

	@property 
	def num_exporters(self):
		pass

	@property 
	def num_importers(self):
		pass

	@property 
	def num_products(self):
		pass


	# ----------------------- #
	# - Data Import Methods - #
	# ----------------------- #

	def from_dataframe(self, df, years):
		"""
		Populate Object from Pandas DataFrame
		"""
		#-Force Interface Variables-#
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(df.columns)
			for item in self.interface['default']:
				if item not in columns: 
					raise TypeError("Need %s to be specified in the incoming data" % item)
			#-Set Attributes-#
			self.__data = df.set_index(self.interface['default'][:-1]) 	#Index by all values except 'value'
			self.years = years
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns:\n\t%s" % self.interface['default'])
		return self


	def from_constructor(self, source_dir, years=[], verbose=True):
		"""
		Construct Object From Constructor Class [Default Dataset ONLY][1]
		
		Notes
		-----
		[1] If wanting to create custom Dataset then use NBERFeenstraWTFConstructor Class
		"""
		return NBERFeenstraWTFConstructor(source_dir=source_dir, years=years, default_dataset=True, verbose=verbose)

	def from_pickle(self, fl):
		"""
		Populate Object from Pickle File 
		"""
		raise NotImplementedError

	def from_hd5py(self, fl):
		"""
		Populate Object from hd5py File
		"""
		raise NotImplementedError

	# -------------------------------- #
	# - Country / Aggregates Filters - #
	# -------------------------------- #

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

	# -------------------------- #
	# - Exports / Imports Data - #
	# -------------------------- #

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







## - In WORK - ##

# - SubClasses of NBERFeenstraWTF - #

class NBERFeenstraWTFExport(NBERFeenstraWTF):
	"""
	Export Data Class
	"""
	pass

class NBERFeenstraWTFImport(NBERFeenstraWTF):
	"""
	Import Data Class
	"""
	pass