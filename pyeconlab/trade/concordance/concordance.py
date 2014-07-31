"""
Concordances for TradeSystem

NBER-FEENSTRA 	{importer : iso3c}
				{exporter : iso3c}

Note: This whole project should be updated to be a tradesystem package so that I can have classifications 
in a folder
"""

from NBERFeenstraWTF import CountryCodeToISO3C

import numpy as np

# Is this a utility? -#

def concord_data(concordance, item, return_error=True):
	"""
	Function for Parsing Concordance Dictionaries
	
	Input:
	------ 
			concordance 	: 	dict
			item 			:	dict keys
			
	Options:
	--------
		return_error 	: 	True/False or Value
							True 	Raise ValueError if key is not found in concordance
							False 	Return np.nan if key is not found in concordance
							Value 	Specify a Return Value if no Match
	"""
	try:
		return concordance[item]
	except:
		if return_error == True:
			raise ValueError('[Error] %s is not found in the concordance' % item)
		elif return_error == False:
			return np.nan
		else:
			return return_error 	# Can Specify a Return Code


