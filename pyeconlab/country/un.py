"""
United Nations Country Information

Contains
--------
UNCountryCodes 	: 	Wrapper for UN Country Codes Data (ISO3C, ISO3N, Names)

"""

import pandas as _pd
import pyeconlab.util as _util

from .base_countrycodes import CountryCodes

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

	Future Work
	-----------
	[1] Meta Data Constructor for ./meta/

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
		self._fn 		= u"unstats_CountryCodeAndNameToISO2ISO3.xls"
		self._md5hash 	= u"332efad5c0c03064658fbd35c40646b0"
		self._fl 		= _util.package_folder(__file__, "data") + self._fn

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

