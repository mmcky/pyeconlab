"""
CEPII/BACI Dataset Objects

Supporting Constructor
----------------------
[1] BACIConstructor

Dependancies
------------
[1] pyeconlab.trade => CPTradeDataset, CPTradeData, CPExportData, CPImportData

Product Classification
----------------------
[1] HS92 Years: 1995-2011
[2] HS96 Years: 1998-2011
[3] HS02 Years: 2003-2011

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
from .meta import BACI
from pyeconlab.trade.dataset import CPTradeDataset, CPTradeData, CPExportData, CPImportData


class BACITradeData(CPTradeData, BACI):
	""" BACI TRADE Dataset """
	pass

class BACIExportData(CPExportData, BACI):
	""" BACI Export Dataset """
	pass

class BACIImportData(CPImportData, BACI):
	""" BACI Import Dataset """
	pass