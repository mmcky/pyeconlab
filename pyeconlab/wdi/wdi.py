"""
WDI Object Code
Handles the interaction with WDI Data Files

Dependancies:
------------
[1] MyDatasets Library for Dataset Management
"""

### --- Standard Library Imports --- ###

import os
import sys
import pickle
import re
import pandas as pd
import itertools as it
import pprint

from .meta import WDISeriesCodes, CodeToName
codes = WDISeriesCodes()

### --- WDI Data Class --- ###

#  source_dir="D:/work-data/datasets/d1352f394ef8e7519797214f52ccd7cc/" (current local address)

class WDI(object):
	"""
	Key Assumption: WDI_data.csv is the file from the WDI and format hasn't changed

	Data Structure:
		[1] Core Data Structure is Wide pd.DataFrame as it is more memory efficient
			(iso3c, series_code) 	|	< ..... years .... >

	Notes:
		[1] How should I apply year filter?
		**> (a) As a Year Filter on Wide and Long Data: def year_filter(years=(syear, eyear), dta_struc='wide'/'long')
			(b) Build into each relevant function

	Future Work:
		[1] Make more robust to changes in the source dataset (Declare File Interface Settings)
		[2] Allow a source to be the WDI file rather than just source_ds
		[3] Integrate pprint objects for better output
	"""

	## -- Source Data -- ##
	source_dir = ""	
	## -- WDI Data -- ##
	data = None 							#Data is by default Wide for Efficient Storage
	country_codes = None
	country_names = dict() 
	series_codes = None			
	series_descriptions = dict()
	## -- Year Attributes -- ##
	start_year = None
	end_year = None
	#- Simple Codes -#
	codes = WDISeriesCodes()
	## -- Pickle Storage -- ##
	pickle = None 

	## -- Setup and Initialise -- ##

	def __init__(self, source_dir, verbose=True): 								#Default - Verbosely setup WDI Object
		self.source_dir = source_dir
		## -- Load Data -- ##
		self.data = pd.read_csv(self.source_dir + 'WDI_Data.csv') 						#Assume Relative Reference to File given as FN
		self.from_df(self.data)
		self.start_year = self.data.columns[0]
		self.end_year = self.data.columns[-1]
		if verbose: print "\n[INFO] Setup of WDI() is complete!\n"
		
	## -- Object Information -- ##

	def info(self):
		''' Provide Summary Information of the WDI Object '''
		print "\nWDI Object Summary Information\n"
		print "\twdi.data (Rows: %s, Columns: %s)" % self.data.shape
		print "\twdi.data.index.names: %s" % self.data.index.names
		print "\twdi.data.columns.names: %s" % self.data.columns.names
		print "\twdi.start_year: %s" % self.start_year
		print "\twdi.end_year: %s" % self.end_year
		print

	## -- IO -- ##

	def from_df(self, df, verbose=False):
		''' Setup WDI Object from pd.DataFrame
			Incoming Format: Wide (iso3c, series_code) : years
		'''
		# Rename Vars #
		cols = list(df.columns)
		cols[0] = 'name' 													#WARNING: Currently assume this order from the file for the first 4 columns
		cols[1] = 'iso3c'	
		cols[2] = 'series_description'
		cols[3] = 'series_code'	
		df.columns = pd.Index(cols)
		# Set Meta Data #
		tmp = df[['name', 'iso3c']].copy(deep=True).drop_duplicates()
		for idx, s in tmp.iterrows():
			self.country_names[s['iso3c']] = s['name']
		self.country_codes = sorted(self.country_names.keys())
		tmp = df[['series_code', 'series_description']].copy(deep=True).drop_duplicates()
		for idx, s in tmp.iterrows():
			self.series_descriptions[s['series_code']] = s['series_description']
		self.series_codes = sorted(self.series_descriptions.keys())
		del tmp
		# Remove Saved Meta Data from Data Table #
		del df['name']
		del df['series_description']
		# Set Index #
		df.set_index(keys=['iso3c', 'series_code'], inplace=True)
		df.columns.names = ['year']
		return df 														#Q: Should this set self.data?

	## -- Getter Methods -- ##

	def get(self, cntry, series_code, year, verbose=False):
		'''
			Retrieve a data value for Country, Series_Code and Year
		'''
		idx = (cntry, series_code)
		return self.data.get_value(idx, year)

	## -- Filters -- ##

	def year_filter(self, years, verbose=False):
		''' 
			Filter WDI Object for Years
			Assume: Core Data Structure (Wide) with Columns as Years
			Returns Data and resets the object to be within certain years
		'''
		if type(years) == tuple:
			start_year, end_year = years
			if verbose: print "[Year Filter] Start Year: %s and End Year: %s" % (start_year, end_year)
			yearlist = [str(x) for x in range(start_year, end_year+1, 1)]										#Note: +1 for Inclusive Years! Not in Python Convention
		elif type(years) == slice:
			start_year, end_year, step = (years.start, years.stop, years.step)
			if verbose: print "[Year Filter] Start Year: %s and End Year: %s and Step: %s" % (start_year, end_year, step)
			yearlist = [str(x) for x in range(start_year, end_year+1, step)] 									#Note: +1 for Inclusive Years! Not in Python Convention
		else:
			raise ValueError("Years is not a tuple or slice")
		## -- Reset Data -- ##
		self.data = self.data[yearlist]
		self.start_year = start_year
		self.end_year = end_year
		return self.data

	## -- Data Retrieval -- ##

	def series(self, series_code, cntry=None, verbose=False):
		"""
		Returns a pd.Series() or pd.DataFrame of WDI Series that matches series_code
		Options:
			[1]	 cntry 		Country Filter [Can be List or just a single Country]

		Future Work:
			[1] This should return a pd.Series when only a single country
		"""
		if cntry == None:
			if verbose: print "No country specified ... returning data for ALL countries"
			cntry = self.data.index.levels[0]
		elif type(cntry) == unicode: 								#Should I use unicode utf-8 OR Strings?
			if verbose: print "Converting Unicode Country (%s) to ASCII String" % cntry
			cntry.encode('ascii', 'ignore')
		elif type(cntry) != list:
			if verbose: print "Returning Series for Country: %s, and Series: %s" % (cntry, series_code)
			name = cntry + "-" + series_code
			s = self.data.xs(cntry).xs(series_code)
			s.name = name
			return s
		if verbose: print "Returning Series: %s for Countries: %s" % (series_code, cntry)
		idx = list(it.product(cntry, [series_code]))
		return self.data.ix[idx]
	
	def series_long(self, series_code, verbose=False):
		"""
		Returns a DataFrame of WDI Series that matches series_codes
	
			[1] series_code 	: 	code or list(code)		

		"""
		if type(series_code) == str:
			series_code = [series_code]
		for idx, code in enumerate(series_code):
			data = self.series(code, cntry=None, verbose=verbose).reset_index()
			del data['series_code']
			data = data.set_index(['iso3c']).stack()
			data = pd.DataFrame(data, columns=[CodeToName[code]])
			if idx == 0:
				df = data
			else:
				df = df.merge(data, left_index=True, right_index=True)
		return df

	def year_data(self, year, verbose=False):
		''' Return Year Specific Data 
			Input:
				year 	int(), str() or list(int() or str())
		'''
		if type(year) == str or int:
			return wdi.data[str(year)]
		elif type(year) == list:
			return wdi.data[[str(x) for x in year]]
		else:
			raise ValueError("year must be str; int or a list of str; int")

	def cntry_series(self, series_code, cntry, verbose=False):
		''' A simple wrapper for single country series '''
		return self.series(series_code, cntry=cntry, verbose=verbose)

	def cntry_data(self, cntry, series_codes=None, verbose=False):
		'''
			Find Country Data
		'''
		if series_codes == None:
			return self.data.ix[cntry] 						#All Series Codes Available in Dataset
		else:
			return self.data.ix[cntry].ix[series_codes] 	#Only Specified Series

	def lookup_series(self, regexp, verbose=False):
		''' Lockup Possible Series Codes '''
		exp = re.compile(regexp)
		results = []
		for sc in self.series_descriptions.keys():
			if re.search(exp, self.series_descriptions[sc]):
				results.append((sc, self.series_descriptions[sc]))
		## -- Error Handling -- ##
		if len(results) == 0:
			raise ValueError("Nothing matched the regex: %s") % regexp
		return results

	### --- Visualisation and Plotting --- ###

	def ts_plot(series_code, cntry, start_year=None, end_year=None, verbose=False):
		## -- Option Parsing -- ##
		if start_year == None:
			pass
		if end_year == None:
			pass
		## -- Plotting -- ##
		raise NotImplementedError




### --- Test Scripts --- ###

if __name__ == '__main__':
	print "WDI Library Test Script"
	print
	W = WDI('WDI_Data.csv',source_ds='d1352f394ef8e7519797214f52ccd7cc', hash_file_sep=r' ', verbose=True)
	# - Test Info Method - #
	W.info()
	
	# - Test Series Function - #
	print
	print "Testing series() method"
	s = W.series(r'NY.GDP.MKTP.CD', verbose=True)
	print s[0:10]
	s = W.series(r'NY.GDP.MKTP.CD', cntry=['AFG', 'ZWE'], verbose=True)
	print s
	s = W.series(r'NY.GDP.MKTP.CD', cntry='AUS', verbose=True)
	print s

	# - Test get Function - #
	print
	print "Testing get() method"
	v = W.get('AUS', r'NY.GDP.MKTP.CD', '2000')
	print "Value: %s" % v

	# - Test lookup_series function - #
	print
	print "Testing lookup_series() method"
	r = W.lookup_series(r'GDP per capita growth')
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(r)

	# - Year Filter - #
	print
	print "Testing year_filter() method"
	print "Current WDI Object Info:"
	W.info()
	W.year_filter(years=(2001,2002), verbose=True)
	print "Year Filter Info"
	W.info()
