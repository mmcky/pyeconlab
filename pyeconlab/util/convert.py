'''
	Construct Python Files from Pandas Objects
'''

import pandas as pd

def from_series_to_pyfile(series, target_dir='data/', fl=None, docstring=None):
	'''
		Construct a .py file from a Pandas Series Object

		s = pd.Series([1,2,3,4])

		will write a file with:  s.name = [1,2,3,4]
	'''
	if type(series) != pd.Series:
		raise TypeError("series: must be a pd.Series")
	doc_string = u'\'\'\'\n\t%s\n\'\'\'\n\n' % docstring 	# DocString
	items = u'%s = [' % series.name.replace(' ', '_')		# Replace spaces with _
	for idx, item in enumerate(series.values):
		# - Spacing for Vertical List of Items - #
		if idx == 0:
			tabs = 1
		else:
			tabs = 4
		items += '\t'*tabs + '\'' + '%s'%item + '\''  + ',' + '\n'
	doc = doc_string + items[:-1] + ']\n'
	if fl == None:
		return doc	 
	else:
		# Write to Disk #
		f = open(target_dir+fl, 'w')
		f.write(doc)
		f.close()


	
