"""
Construct Python Files from Pandas Objects
Should These be in files.py?
"""

import pandas as pd

def from_series_to_pyfile(series, target_dir='data/', fl=None, docstring=None):
	"""
	Construct a .py file from a Pandas Series Object 
	[Warning: Ensure `series` is named what you would like the variable to be]

	Arguments
	---------
	series 		: 	pd.Series (that has an index)
	target_dir 	: 	target directory to save file
	fl 			: 	filname
	docstring 	:	specify a docstring at the top of the file	 

	Example
	-------

	s = pd.Series([1,2,3,4])

	will write a file with:  s.name = [	1,
										2,
										...
									  ]
	"""
	if type(series) != pd.Series:
		raise TypeError("series: must be a pd.Series")
	doc_string = u'\"\"\"\n%s\nManual Check: <date>\n\"\"\"\n\n' % docstring 	# DocString
	items = u'%s = [' % series.name.replace(' ', '_')							# Replace spaces with _
	once = True
	for idx, item in enumerate(series.values):
		# - Newline and Tabbed Spacing for Vertical List of Items - #
		tabs = 4
		if once == True:
			items += "\n"
			once = False
		items += '\t'*tabs + '\'' + '%s'%item + '\''  + ',' + '\n'
	doc = doc_string + items + ']\n'
	if type(fl) in [str, unicode]:
		# Write to Disk #
		f = open(target_dir+fl, 'w')
		f.write(doc)
		f.close()			 
	else:
		return doc



def from_idxseries_to_pydict(series, target_dir='data/', fl=None, docstring=None, verbose=False):
	"""
	Construct a .py file containing a Dictionary from an Indexed Pandas Series Object
	[Warning: Ensure `series` is named what you would like the variable to be]

	Arguments
	---------
	series 		: 	pd.Series (that has an index)
	target_dir 	: 	target directory to save file
	fl 			: 	filname
	docstring 	:	specify a docstring at the top of the file	 
	fl 			:  filename

	Example
	-------

	s.name = { 	index : value,
				... etc.
			 }
	"""
	if type(series) != pd.Series:
		raise TypeError("series: must be a pd.Series with an Index")
	docstring = u'\"\"\"\n%s\nManual Check: <date>\n\"\"\"\n\n' % docstring 	# DocString
	items = u'%s = {' % series.name.replace(' ', '_')							# Replace spaces with _
	once = True
	for idx, val in series.iteritems():
		# - Newline and Tabbed Spacing for Vertical List of Items - #
		tabs = 4
		if once == True:
			items += "\n"
			once = False
		items += '\t'*tabs + '\'' + '%s'%idx + '\''  + ' : ' + '\'' + '%s'%val + '\'' + ',' + '\n'
	doc = docstring + items + '}\n'
	if type(fl) in [str, unicode]:
		# Write to Disk #
		if verbose: print "[INFO] Writing file: %s" % (target_dir+fl)
		f = open(target_dir+fl, 'w')
		f.write(doc)
		f.close()
	else:
		return doc	
		