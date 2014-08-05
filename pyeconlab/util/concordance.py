"""
Concordance Utilities
"""

import pandas as pd
import countrycode as cc

def countryname_concordance(data, concord_vars=('countryname', 'iso3c'), rtn_type='series', verbose=False):
	"""
	Compute a Country Name Concordance using package: pycountrycode
	
	**Note:** pycountrycode is going through a re-write so this will most likely break

	data 			: 	List
	concord_vars 	: 	Variables to Concord From Data
						Currently Supported:
						--------------------
						'countryname' => 'iso3c'
						'countryname' => 'iso3n'
	rtn_type 		: 	dict or indexed pd.Series					

	Future Work
	-----------
	[1] Build Internal CountryCode Routines
	"""
	def replace_nonstring(items):
		for idx, code in enumerate(items):
			if type(code) != str:
				items[idx] = '.'
		return items

	def reject_non3digit(items):
		for idx, code in enumerate(items):
			if len(code) != 3:
				items[idx] = '.'
		return items

	if type(data) != list:
		raise TypeError("data: needs to be a list")
	#-Find Set Of Countries-#
	if type(data) == list:
		countrynames = list(set(data))
	if concord_vars[1] == 'iso3c':
		iso3c = cc.countrycode(codes=countrynames, origin='country_name', target='iso3c')
		iso3c = replace_nonstring(iso3c) 													#Could use lambda functions
		iso3c = reject_non3digit(iso3c)														#Could use lambda functions
		concord = pd.Series(iso3c, index=countrynames, name='iso3c')
		concord.index.name = 'countryname'
		concord.sort()
	if concord_vars[1] == 'iso3n':
		iso3n = cc.countrycode(codes=countrynames, origin='country_name', target='iso3n')
		iso3n = replace_nonstring(iso3n)
		iso3n = reject_non3digit(iso3n)
		concord = pd.Series(iso3n, index=countrynames, name='iso3n')
		concord.index.name = 'countryname'
		concord.sort()
	#-Parse rtn_type-#
	if rtn_type == 'series':
		return concord
	else:
		return concord.to_dict()