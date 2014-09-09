"""
ISO3166 Country Codes Class

[1] Useful in aquiring a list of official countries

"""

try:
	import xmltodict
except ImportError:
	raise ImportError("Cannot import xmltodict - try installing with pip install xmltodict")

import pandas as _pd

import pyeconlab.util as _util
from .base_countrycodes import CountryCodes

class ISO3166(CountryCodes):
	""" 
	ISO3166 Data Object
	
	DataSource:
	----------
	./data/linuxmint16_iso_3166.xml (md5hash = ae467df20f32c089da909dd27191cf7d)
		Source: 			Linux Mint 16 (/usr/)
		Downloaded: 		06/08/2014
		Original FileName: 	iso_3166.xml
		Original md5hash: 	ae467df20f32c089da909dd27191cf7d
	"""
	def __init__(self, verbose=True):
		"""
		Initialise Class and Populate with Data From Package

		Future Work
		-----------
		[1] Add md5 checksum check

		"""
		# - Attributes - #
		self.__fn 		= u"linuxmint16_iso_3166.xml"
		self.__fl 		= _util.package_folder(__file__, "data") + self.__fn

		# - Acquire Data From Package - #
		if verbose: print '[INFO] Loaded Country Codes from iso_3166 xml file %s \nLocation: %s\n' % (self.__fn, self.__fl)
		xml 	= xmltodict.parse(open(self.__fl))
		data = _pd.DataFrame()
		for item in xml['iso_3166_entries']['iso_3166_entry']:
			iso2c = item['@alpha_2_code']
			iso3c = item['@alpha_3_code']
			iso3n = item['@numeric_code']
			name  = item['@name']
			try:
				official_name = item['@official_name']
			except: 
				official_name = ''
			row = {'iso2c' : iso2c, 'iso3c' : iso3c, 'iso3n' : iso3n, 'countryname' : name, 'official_name' : official_name}
			data = data.append(row, ignore_index=True)

		# - Recode Data - #
		self.data = data
