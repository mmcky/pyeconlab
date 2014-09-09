"""
Generic Country Code Classes and Methods
"""

import pandas as _pd

class CountryCodes(object):
	"""
	SuperClass for CountryCode Datasets (such as in un.py)
	Contains Common Properties and Methods for CountryCode Objects

	Interface
	---------
	data attribute must contain => ['iso3c', 'iso3n', 'countryname']

	Notes:
	-----
	[1] For country data that isn't standard (like iso3c, iso3n etc.) 
		then individual classes or methods will need to be implemented in a Child Object.

	Future Work
	-----------
	[1] Improve Error Handling
	[2] Improve interface enforcement
	"""
	
	data = _pd.DataFrame
	interface = ['iso3c', 'iso3n', 'countryname']

	#-Properties-#
	@property 
	def num_iso3c(self):
		return len(self.data['iso3c'].dropna())

	#-Series Properties-#

	@property 
	def iso3c(self):
		return list(self.data['iso3c'].dropna()) 			#Some Countries don't have official iso3c codes in some incomplete datasets

	@property
	def iso3n(self):
		return list(self.data['iso3n'].dropna())

	#-Generate Concordance Dictionaries-#

	@property 
	def name_to_iso3c(self):
		concord = self.data[['iso3c', 'countryname']].dropna().set_index('countryname') 	#Drop Codes with No Pair
		return concord['iso3c'].to_dict()

	@property 
	def iso3c_to_name(self):
		concord = self.data[['iso3c', 'countryname']].dropna().set_index('iso3c') 			#Drop Codes with No Pair
		return concord['countryname'].to_dict()

	@property 
	def iso3n_to_iso3c(self):
		concord = self.data[['iso3c', 'iso3n']].dropna().set_index('iso3n') 				#Drop Codes with No Pair
		return concord['iso3c'].to_dict()

	@property 
	def iso3c_to_iso3n(self):
		concord = self.data[['iso3c', 'iso3n']].dropna().set_index('iso3c') 				#Drop Codes with No Pair
		return concord['iso3n'].to_dict()

	@property 
	def name_to_iso3n(self):
		concord = self.data[['iso3n', 'countryname']].dropna().set_index('countryname') 	#Drop Codes with No Pair
		return concord['iso3n'].to_dict()

	@property 
	def iso3n_to_name(self):
		concord = self.data[['iso3n', 'countryname']].dropna().set_index('iso3n') 			#Drop Codes with No Pair
		return concord['countryname'].to_dict()