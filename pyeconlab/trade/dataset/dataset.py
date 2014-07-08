'''
	Dataset Construction Classes

	Datasets:
	--------
		1. Feenstra/NBER Data 
		2. BACI Data
		3. CEPII Data
		4. UNCTAD Revealed Capital,Labour, and Land

	Issues:
	-------
		1. 	How best to Incorporate the Source Dataset files. They can be very large 
			[Currently will pull in from a MyDatasets Object]
		2. 	This will be pretty slow to derive data each time from the raw data and will drive unnecessary wait times
			(i.e. Probably Need NBERPreCompiled and NBER Classes)


	Future Work:
	-----------
		1. How to Handle Custom Altered Made Datasets such as Intertemporally Consistent NBER-BACI Data?
'''

# Packages #
import pandas as pd

class NBERFeenstraWTF(object):
	'''
		Data Object for Feenstra NBER World Trade Data
		Years: 1962 to 2000
		Classification: SITC R2 L4
		Notes: Pre-1974 care is required for constructing intertemporally consistent data

		Interface:
		---------
		Files: 	wtf##.dta where ## is 62-00 	[03/07/2014]

		Future Work:
		-----------
			[1] Update Pandas Stata to read older .dta files (then get wget directly from the website)
	'''

	# - Attributes - #
	name 			= 'Feenstra (NBER) World Trade Dataset'
	available_years = range(1962, 2000, 1)
	classification 	= 'SITC'
	revision 		= 2
	level 			= 4
	source_web 		= u"http://cid.econ.ucdavis.edu/nberus.html"
	raw_units 		= 1000
	raw_units_str 	= u'US$1000\'s'
	interface 		= ['year', 'exporteriso3c', 'importeriso3c', 'productcode', 'value', 'quantity']

	def __init__(self, df, verbose=False):
		''' 
			Load RAW Data from Preserved Dataset or call NBERFeenstraConstructor() Object
			
			Interface:
			--------- 
				self.interface
		'''
		if type(df) == pd.DataFrame:
			# - Check Incoming Data Conforms - #
			columns = set(data.columns)
			for item in self.interface:
				if item not in columns: raise TypeError("Need %s to be specified in the incoming data") % item
			self.data = df.reindex_axis(self.interface, axis=1) # Check this brings data with it #
		else:
			raise TypeError("data must be a dataframe that contains the following interface columns: %s" % self.interface)

	## - Country / Aggregates Filters - ##

	def country_data(self):
		pass

	def world_data(self):
		pass

	def geo_aggregates(self, members):
		'''	
			members = dict {'iso3c' : 'region'}
			Subsitute Country Names for Regions and Collapse.sum()
		'''
		pass 

	## - Exports / Imports Data - ##

	def export_data(self):
		'''
			Extract Export Data from Raw Data
		'''
		from pyeconlab.trade.concordance import NBERFeenstraExportersToISO3C, concord_data
		
		expdata = self.raw_data[['year', 'exporter', 'sitc4', 'value']]
		cntrynotfound = []
		expdata['exporter'] = expdata['exporter'].apply(lambda x: concord_data(NBERFeenstraExportersToISO3C, x))

		### --- Working Here --- #

		self.exports = expdata
		return self.exports

	def import_data(self):
		pass


######## - IN WORK - ##########

class BACI(object):
	pass

class CEPII(object):
	pass

