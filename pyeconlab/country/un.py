"""
UN Country Codes Information

Organisation
------------
[1] SuperClass
	CountryCodes 	: 	SuperClass for Common Methods

[2] ChildClasses 
	UNCountryCodes 	: 	Wrapper for UN Country Codes Data

"""

import pandas as _pd
import pyeconlab.util as _util

class CountryCodes(object):
	"""
	SuperClass for CountryCode Datasets
	Contains Common Properties and Methods to CountryCode Objects

	Interface
	---------
	data attribute must contain => ['iso3c', 'iso3n', 'countryname']

	Notes:
	-----
	[1] For Data that isn't standard (like UN countrycodes) then individual methods will need to be implemented

	Future Work
	-----------
	[1] Improve Error Handling
	"""
	
	data = _pd.DataFrame

	# - Properties - #
	@property 
	def num_iso3c(self):
		return len(self.data['iso3c'].dropna())

	# - Series Properties - #

	@property 
	def iso3c(self):
		return list(self.data['iso3c'].dropna()) 			#Some Countries don't have official iso3c codes

	# - Generate Concordance Dictionaries - #

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
		return concord['iso3n'].to_dict()



class UNCountryCodes(CountryCodes):
	"""
	United Nations Country Code Classifications

	DataSource:
	----------
	./data/unstats_CountryCodeAndNameToISO2ISO3.xls (md5hash = 332efad5c0c03064658fbd35c40646b0)
		Source: 			http://unstats.un.org/unsd/tradekb/Knowledgebase/Comtrade-Country-Code-and-Name
		Downloaded: 		22-July-2014
		Original FileName: 	Country code and Name ISO3 ISO3.xls
		Original md5hash: 	acf6f39d2a49e1611e929a778a136706

	File Interface:
	---------------
	[Country Code, Country Name English, Country Fullname English, Country Abbrevation, Cty Comments,
		ISO2-digit Alpha, ISO3-digit Alpha, Start Valid Year, End Valid Year]

	Recodes:
	--------
	Country Code 			-> iso3n 				#UN CountryCode = iso3n
	Country Name English 	-> countryname 
	Country Fullname English -> countryfullname
	ISO2-digit Alpha 		-> iso2c
	ISO3-digit Alpha		-> iso3c
	Start Valid Year 		-> startyear
	End Valid Year			-> endyear

	Dropping: 
	--------
	Country Abbrevation, Cty Comments

	Notes
	-----
	[1] Should Numeric Country Codes be String's with Leading Zero's?

	"""

	drop 	= [
		u'Country Abbrevation',
		u'Cty Comments'
	]

	recodes = {
		u'Country Code' 			: 'iso3n',
		u'Country Name English' 	: 'countryname',
		u'Country Fullname English' : 'countryfullname',
		u'ISO2-digit Alpha'			: 'iso2c',
		u'ISO3-digit Alpha' 		: 'iso3c',
		u'Start Valid Year'			: 'startyear',
		u'End Valid Year'			: 'endyear',
	}

	def __init__(self, verbose=True):
		"""
		Initialise Class and Populate with Data From Package

		Future Work
		-----------
		[1] Allow specification of User File
		"""
		# - Attributes - #
		self._fn 	= u"unstats_CountryCodeAndNameToISO2ISO3.xls"
		self._md5hash = u"332efad5c0c03064658fbd35c40646b0"
		self._fl 	= _util.package_folder(__file__, "data") + self._fn
		
		# - Acquire Data From Package - #
		if _util.verify_md5hash(self._fl, self._md5hash):
			self.data 	= _pd.read_excel(self._fl, )
		else:
			raise ValueError("Object's md5hash doesn't match the md5hash of the package data file!")
		if verbose: print '[INFO] Loaded UN Country Codes from file %s \nLocation: %s\n' % (self._fn, self._fl)

		# - Drop Data - #
		for item in self.drop:
			if verbose: print "Dropping: %s" % (item)
			del self.data[item]
		if verbose: print ""

		# - Recode Data - #
		self.data = _util.recode_index(self.data, self.recodes, axis='columns', verbose=verbose)

