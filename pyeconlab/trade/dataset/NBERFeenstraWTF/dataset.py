"""
NBERFeenstraWTF Dataset Object

Supporting Constructor
----------------------
	[1] NBERFeenstraConstructor

Dependancies
------------
	[1] pyeconlab.trade.dataset 
		Dataset, TradeData, ExportData, ImportData

Types
=====
[1] Trade Dataset 	(Bilateral Trade Flows)
[2] Export Dataset 	(Export Trade Flows)
[3] Import Dataset 	(Import Trade Flows)

"""

import pandas as pd
import cPickle as pickle

#-Generic Containers-#
from pyeconlab.trade.dataset import CPTradeDataset, CPTradeData, CPExportData, CPImportData

class NBERFeenstraWTF(CPTradeDataset):
	"""
	Parent NBERFeenstraWTF Class for Trade, Export and Import Objects that contains meta data

	Source Dataset Attributes
	-------------------------
	Years: 			1962 to 2000
	Classification: SITC R2 L4
	Notes: 			Pre-1974 care is required for constructing intertemporally consistent data

	"""

	# - Attributes - #
	name 			= u'Feenstra (NBER) World Trade Dataset'
	available_years = xrange(1962, 2000, 1)
	classification 	= 'SITC'
	revision 		= 2
	level 			= 4
	source_web 		= u"http://cid.econ.ucdavis.edu/nberus.html"
	raw_units 		= 1000
	raw_units_str 	= u'US$1000\'s'

#-------#
#-Trade-#
#-------#

class NBERFeenstraWTFTrade(CPTradeData, NBERFeenstraWTF):
	"""
	NBERFeenstraWTF Bilateral World TRADE Data
	
	Interfaces: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']

	Notes
	-----
	[1] Only set attribute here for it to be local to the class. Other attributes are inherited. 
		If there is an attribute specific to NBERFeenstraWTF TRADE then it should be included here
	"""
		
	#-Data-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	#-Computable Properties-#

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
			return self.__exports
	@imports.setter
	def imports(self, values):
		self.__imports = values

#--------#
#-Export-#
#--------#

class NBERFeenstraWTFExport(CPExportData, NBERFeenstraWTF):
	"""
	NBERFeenstraWTF EXPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""

	#-Data-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	
#--------#
#-Import-#
#--------#

class NBERFeenstraWTFImport(CPImportData, NBERFeenstraWTF):
	"""
	NBERFeenstraWTF IMPORT World Trade Data
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	
	#-Data-#

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

