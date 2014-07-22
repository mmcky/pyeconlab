"""
	DataFrame Utilities
"""

import pandas as pd

def recode_index(df, recode, axis='columns', verbose=True):
	"""
	Recode A DataFrame Index from a Recode Dictionary
	Provide a Summary of Results

	Parameters
	----------
	df 		: 	pd.DataFrame
	recode 	: 	dict('From' : 'To')
	axis 	: 	'rows', 'columns' [Default: 'column']

	Returns
	-------
	pd.DataFrame() with new index

	Future Work
	-----------
	[1] Convert Messages to use Pretty Print For Tabular Output Etc.
	"""
	recode_set = set(recode.keys())
	# - Rows - #
	if axis == 'rows':
		raise NotImplementedError
	# - Columns
	elif axis == 'columns':
		# - Prepare Summary - #
		old_idx = set(df.columns)
		summ_msg = 	"[Recode Column Summary]" + '\n' 										\
					"# of Column Items: %s" % len(old_idx) + '\n' 	\
					"# of Recode Items: %s" % len(recode_set) + '\n'
		# - Changes - #
		common = old_idx.intersection(recode_set)
		summ_msg += "Updates: \n" + \
					"------- \n"
		for item in common:
			summ_msg += "  %s -> %s" % (item, recode[item]) + '\n'
		summ_msg += "------- \n"
		summ_msg += "Number of Changes: %s" % len(common) + '\n'
		# - In Recode but not in Column - #
		remaining_recode = recode_set.difference(old_idx)
		if len(remaining_recode) != 0:
			summ_msg += "Unused Recode Items: %s" % remaining_recode + '\n'
		# - In Column but not in Recode - #
		remaining_column = old_idx.difference(recode_set)
		if len(remaining_column) != 0:
			summ_msg += "Unchanged Column Items: %s" % remaining_recode + '\n'
		if verbose: print summ_msg
		
		# - Perform Rename Operation - #
		df.rename(columns=recode, inplace=True) 		

	else:
		raise ValueError("Axis must be 'rows' or 'columns'")
	return df

# - IN WORK - #

def change_message(old_idx, recode):
	"""
	Prepare a change message

	Parameters
	----------
	old_idx : set(old index)
	recode 	: dict('FROM' : 'TO')
	"""
	pass