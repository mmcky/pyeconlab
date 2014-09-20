"""
NBERWTF Dataset Wrapper Objects

Note: This just provides a more appropriate object name OR something very specific to NBERWTF

Supporting Constructor
----------------------
	[1] NBERFeenstraConstructor

Dependancies
------------
	[1] pyeconlab.trade
		CPTradeDataset, CPTradeData, CPExportData, CPImportData

Types
=====
[1] Trade Dataset 	(Bilateral Trade Flows)
[2] Export Dataset 	(Export Trade Flows)
[3] Import Dataset 	(Import Trade Flows)

"""

import numpy as np
import pandas as pd
import cPickle as pickle

#-Generic Containers-#
from .base import NBERWTF
from pyeconlab.trade.dataset import CPTradeDataset, CPTradeData, CPExportData, CPImportData

#-------#
#-Trade-#
#-------#

class NBERWTFTradeData(NBERWTF, CPTradeData):
	"""
	NBERWTF Bilateral World TRADE Data
	Interfaces: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']
	"""
	#-Class Properties-#

	@property 
	def data(self):
		return self.__data
	# @data.setter
	# def data(self, values):
	# 	self.__data = values

	def set_data(self, value, force=False):
		""" Force Assign New Dataset """
		if force:
			self.__data = value
		else:
			raise ValueError("'force' must be manually set using the force flag")

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

#--------#
#-Export-#
#--------#

class NBERWTFExportData(NBERWTF, CPExportData):
	"""
	NBERWTF EXPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""
	
	@property 
	def data(self):
		return self.__data
	# @data.setter
	# def data(self, values):
	# 	self.__data = values

	def set_data(self, value, force=False):
		""" Force Assign New Dataset """
		if force:
			self.__data = value
		else:
			raise ValueError("'force' must be manually set using the force flag")

	
#--------#
#-Import-#
#--------#

class NBERWTFImportData(NBERWTF, CPImportData):
	"""
	NBERWTF IMPORT World Trade Data
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	
	@property 
	def data(self):
		return self.__data
	# @data.setter
	# def data(self, values):
	# 	self.__data = values
	def set_data(self, value, force=False):
		""" Force Assign New Dataset """
		if force:
			self.__data = value
		else:
			raise ValueError("'force' must be manually set using the force flag")
