"""
NBERFeenstraWTF Dataset Object

Supporting Constructor
----------------------
	[1] NBERFeenstraConstructor

Dependancies
------------ 
	[1] Dataset, TradeData, ExportData, ImportData

Types
=====
[1] Trade Dataset 	(Bilateral Trade Flows)
[2] Export Dataset 	(Export Trade Flows)
[3] Import Dataset 	(Import Trade Flows)

"""

import pandas as pd
import cPickle as pickle

#-Generic Containers-#
from pyeconlab.trade.dataset import TradeDataset, TradeData, ExportData, ImportData

class NBERFeenstraWTF(TradeDataset):
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

class NBERFeenstraWTFTrade(TradeData, NBERFeenstraWTF):
	"""
	Feenstra NBER Bilateral World TRADE Data
	
	Interfaces: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']

	Future Work:
	-----------
	[1] Implement an interface for Quantity Data ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity'], 
	"""
	
	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values


#--------#
#-Export-#
#--------#

class NBERFeenstraWTFExport(ExportData, NBERFeenstraWTF):
	"""
	NBER Feenstra EXPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""

	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

	
#--------#
#-Import-#
#--------#

class NBERFeenstraWTFImport(ImportData, NBERFeenstraWTF):
	"""
	NBER Feenstra IMPORT World Trade Data
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	
	@property 
	def data(self):
		return self.__data
	@data.setter
	def data(self, values):
		self.__data = values

