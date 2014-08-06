"""
Country Concordances

Simple Wrappers for Quickly Obtaining a Country Concordane

Available:
---------
iso3c_to_iso3n
iso3n_to_iso3c

Future Work
-----------
[1] Write a Decorator Function to Sort out source_institution?

"""

from .un import UNCountryCodes

def concordance_data(source_institution, verbose='False'):
	"""
	Select source_institution and return data object
	"""
	if source_institution == 'un':
			return UNCountryCodes(verbose=verbose)
	else:
		raise ValueError("source_institution: only 'un' is currently implemented")

#-Functions-#

def iso3c_to_iso3n(source_institution='un'):
	"""
	ISO3C to ISO3N Mapping Dictionary

	source_institution 		: 	[Default: 'un']

	Notes: 	This will reimport the data from the package xls file but makes a concordance very accessible 
			If using a lot it might be better to import the UNCountryCodes object instead

	Future Work
	-----------
	[1] Have the Option to Import from a meta/iso3c_to_iso3n.py file? Current Execution time is ~20ms
	"""
	return concordance_data(source_institution, verbose=False).iso3c_to_iso3n

def iso3n_to_iso3c(source_institution='un'):
	"""
	ISO3N to ISO3C Mapping Dictionary
	
	Notes: 	This will reimport the data from the package xls file  but makes a concordance very accessible 
			If using a lot it might be better to import the UNCountryCodes object instead

	Future Work
	-----------
	[1] Have the Option to Import from a meta/iso3c_to_iso3n.py file? Current Execution time is ~20ms
	"""
	return concordance_data(source_institution, verbose=False).iso3n_to_iso3c

