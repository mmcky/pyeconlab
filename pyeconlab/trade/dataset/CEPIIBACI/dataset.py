"""
CEPII/BACI Dataset Objects

Supporting Constructor
----------------------
[1] BACIConstructor

Dependancies
------------
[1] pyeconlab.trade => CPTradeDataset, CPTradeData, CPExportData, CPImportData
[2] .base => BACI

Product Classification
----------------------
[1] HS92 Years: 1995-2011
[2] HS96 Years: 1998-2011
[3] HS02 Years: 2003-2011

Types
=====
[1] Trade Data 	(Bilateral Trade Flows)
[2] Export Data 	(Export Trade Flows)
[3] Import Data 	(Import Trade Flows)
"""

import numpy as np
import pandas as pd
import cPickle as pickle

#-Generic Containers-#
from .base import BACI
from pyeconlab.trade.dataset import CPTradeDataset, CPTradeData, CPExportData, CPImportData

#-These are Just Wrappers to Put a more appropriate Class Name Around Generic Dataset Objects and to provide source details	-#
#-May want to hide some source details as they clutter the . namespace 														-#

class BACITradeData(BACI, CPTradeData):
	""" BACI TRADE Dataset """
	pass

class BACIExportData(BACI, CPExportData):
	""" BACI Export Dataset """
	pass

class BACIImportData(BACI, CPImportData):
	""" BACI Import Dataset """
	pass