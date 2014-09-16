"""
NBERWTF Dataset Object

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

class NBERWTFTrade(NBERWTF, CPTradeData):
	"""
	NBERWTF Bilateral World TRADE Data
	Interfaces: ['year', 'eiso3c', 'iiso3c', 'productcode', 'value']
	"""
	pass

#--------#
#-Export-#
#--------#

class NBERWTFExport(NBERWTF, CPExportData):
	"""
	NBERWTF EXPORT World Trade Data
	Interface: ['year', 'eiso3c', 'productcode', 'value']
	"""
	pass

	
#--------#
#-Import-#
#--------#

class NBERWTFImport(NBERWTF, CPImportData):
	"""
	NBERWTF IMPORT World Trade Data
	Interface: ['year', 'iiso3c', 'productcode', 'value']
	"""	
	pass

