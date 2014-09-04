"""
CEPII/BACI Dataset Object

Supporting Constructor
----------------------
	[1] BACIConstructor

Dependancies
------------
	[1] pyeconlab.trade
		CPTradeDataset, CPTradeData, CPExportData, CPImportData

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
from pyeconlab.trade.dataset import CPTradeDataset, CPTradeData, CPExportData, CPImportData


class BACI(CPTradeDataset):
	"""
	Parent NBERFeenstraWTF Class for Trade, Export and Import Objects that contains meta data

	Source Dataset Attributes
	-------------------------
	Years: 			Various ('HS92' : 1995 to 2011, 'HS96' : 1998 to 2011, 'HS02' : 2003 to 2011)
	Classification: Harmonised System (HS)
	Supplementary Data: 	Dataset contains country_concordance and product_classification

	Notes
	-----
	[1] Updatable attributes allow easy updating to new dataset releases from CEPII
	"""

	#-Updatable Attributes-#
	END_YEAR = { 'HS92' : 2012, 'HS96' : 2012, 'HS02' : 2011 } 

	#-Attributes-#
	name 						= u'CEPII BACI Trade Dataset'
	available_years 			= {'HS92' : xrange(1995, END_YEAR['HS92'], 1), 'HS96' : xrange(1998, END_YEAR['HS96'], 1), 'HS02' : xrange(2003, END_YEAR['HS02'],1)} 
	available_classification 	= ['HS92', 'HS96', 'HS02'] 
	available_revisions 		= ['1992']
	source_web 					= u"http://www.cepii.fr/cepii/en/bdd_modele/presentation.asp?id=1"
	source_last_checked 		= np.datetime64('2014-09-03')
	complete_dataset 			= False
	raw_units 					= 1000
	raw_units_str 				= "US$1000's"
	interface 					= {'t' : 'year', 'i' : 'eiso3n', 'j' : 'iiso3n', 'v' : 'value', 'q' : 'quantity'}
	deletions 					= ['a']

	#-Dataset Concordances-#

	country_data_fn = {
		'HS92' 	: 'country_code_baci92.csv',
		'HS96' 	: 'country_code_baci96.csv',
		'HS02' 	: 'country_code_baci02.csv'
	}
	product_data_fn = {
		'HS92' 	: 'product_code_baci92.csv',
		'HS96' 	: 'product_code_baci96.csv',
		'HS02' 	: 'product_code_baci02.csv'
	}

	#-Set within Init-#

	classification  = None 		#'HS92', 'HS96', 'HS02'
	revision 		= None
	level 			= None

	#-HDF File Versions-#
	raw_data_hdf_fn = {
		'HS92' : 'baci92_1995_%s.h5' % (END_YEAR['HS92']),
		'HS96' : 'baci96_1998_%s.h5' % (END_YEAR['HS96']),
		'HS02' : "baci02_2003_%s.h5"%(END_YEAR['HS02'])
	}
	
	raw_data_hdf_yearindex_fn = {
		'HS92' : 'baci92_1995_%s_yearindex.h5' % (END_YEAR['HS92']),
		'HS96' : 'baci96_1998_%s_yearindex.h5' % (END_YEAR['HS96']),
		'HS02' : "baci02_2003_%s_yearindex.h5"%(END_YEAR['HS02'])
	}