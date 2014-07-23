"""
	DataFrame Utilities
"""

import copy
import pandas as pd
import numpy as np


def recode_index(df, recode, axis='columns', inplace=True, verbose=True):
	"""
	Recode A DataFrame Index from a Recode Dictionary
	Provide a Summary of Results

	Parameters
	----------
	df 		: 	pd.DataFrame
	recode 	: 	dict('From' : 'To')
	axis 	: 	'rows', 'columns' [Default: 'column']
	inplace : 	True/False [Default: True]

	Returns
	-------
	pd.DataFrame() with new index

	Future Work
	-----------
	[1] Convert Messages to use Pretty Print For Tabular Output Etc.
	[2] Construct a merge function that behaves similarly to Stata "merge"
	"""

	# - Parse Inplace Option - #
	if inplace == False:
		df = copy.deepcopy(df)
	recode_set = set(recode.keys())
	# - Rows - #
	if axis == 'rows':
		# - Working HERE - #
		raise NotImplementedError
		# - Working HERE - #
	# - Columns
	elif axis == 'columns':
		# - Prepare Summary - #
		old_idx = set(df.columns)
		summ_msg = 	"[Recode Column Summary]" + '\n' 				\
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
			summ_msg += "Unchanged Column Items: %s" % remaining_column + '\n'
		if verbose: print summ_msg
		
		# - Perform Rename Operation - #
		df.rename(columns=recode, inplace=True) 		

	else:
		raise ValueError("Axis must be 'rows' or 'columns'")
	return df


# - IN WORK - #

def merge_report(ldf, rdf, on, verbose):
	"""
	Return a Merge Report
	"""
	pass

def merge_columns(ldf, rdf, on, collapse_columns=('value_x', 'value_y', 'value'), dominant='right', output='final', verbose=True):
	"""
	Merge a LEFT and RIGHT DataFrame on a set of columns and merge columns _x and _y specified in columns
	via a dominant rule. 

	Parameters
	----------
	on 		: 	list of items to merge on (common to both dataframes)
	column 	: 	Merge a Column to a Single Column Matched by on
	collapse_columns : 	After Performing Outer Merge Collapse Columns (LEFT, RIGHT, FINAL)
						Note: This is disaggregated to allow great flexibility on L,R columns that don't share the same pre-word.
	dominant : 	'right'/'left' [Default: 'right'] Anything else will return a list the CONFLICTS
	output 	: 	'final'/'stages' [Default: 'final'] 

	Future Work
	-----------
	[1] Could Change this to allow lists(collapse_columns)
	[1] Write Tests

	"""
	#-Parse collapse_columns-#
	left_col, right_col, final_col = collapse_columns
	
	#-Number of Observations in Both-#
	num_ldf = len(ldf)
	num_rdf = len(rdf)
	
	#-Inner Merge-#
	inner = ldf.merge(rdf, how='inner', on=on)
	num_matched = len(inner)							#Number of Inner Matches
	# Compute Relative to Inner Merge - #
	num_new_obs_from_right = num_rdf - num_matched
	num_old_obs_from_left = num_ldf - num_matched
	
	#-Compute Outer Merge-#
	outer = ldf.merge(rdf, how='outer', on=on)
	#Construct Final Merged Columns
	#-New Observations from Right-#
	outer[final_col] = np.where(outer[left_col].isnull(), outer[right_col], outer[left_col]) 		#Bring in NEW Observations, Else Return Old Observations
	#-Manage Conflicts-#
	right = ldf.merge(rdf, how='right', on=on)[[left_col, right_col]].dropna()
	if dominant.lower() == 'right':
		num_discarded_from_right = 0
		num_overwrite_from_right = len(right[right[left_col] != right[right_col]])
		num_equal_left_right = len(right[right[left_col] == right[right_col]])
			## --> REMOVE <-- ##
			# - Fill Missing RIGHT_COL Values with Final Values - #
			#outer['tmp_right_col'] = np.where(outer[right_col].isnull(), outer[final_col], outer[right_col])
			# - Update Unequal Values in Final Column with Right Values - #
			#outer[final_col] = np.where(outer[final_col] != outer['tmp_right_col'], outer['tmp_right_col'], outer[final_col])
			## -------------- ##
		outer[final_col] = np.where(outer[right_col].isnull(), outer[final_col], outer[right_col])
	elif dominant.lower() == 'left':
		# - This is the default state in initial construction of outer [final_col] Merging New Observations - #
		num_discarded_from_right = len(right[right[left_col] != right[right_col]])
		num_overwrite_from_right = 0
		num_equal_left_right = len(right[right[left_col] == right[right_col]])
	else:
		# Show Conflict and Quit - #
		print "[ERROR] Cannot Resolve Conflicts!"
		right = ldf.merge(rdf, how='right', on=on).dropna(subset=[left_col,right_col])
		conflicts = right[right[left_col] != right[right_col]][on + [left_col, right_col]]
		print conflicts[0:10]
		return conflicts

	#-Write Report-#
	report = 	u"MERGE Report [Rule: %s]\n" % dominant									+ \
				u"------------\n" 														+ \
				u"# of Left Observations: \t%s\n" % (num_ldf) 							+ \
				u"# of Right Observations: \t%s\n" % (num_rdf) 							+ \
				u"# of Total Observations: \t%s\n" % (num_ldf + num_rdf) 				+ \
				u"  `ON` Matched Observations: \t%s\n" % (num_matched) 						+ \
				u"\n" 																	+ \
				u"LEFT [%s] STATS:\n" % left_col 										+ \
				u"----------\n" 														+ \
				u"# of Unmatched (Old) Observations (from LEFT): \t\t%s\n" % (num_old_obs_from_left) + \
				u"# of Right values DISCARDED in preference of Left: \t%s\n" % (num_discarded_from_right) + \
				u"\n" 																	+ \
				u"RIGHT [%s] STATS:\n" % right_col 										+ \
				u"----------\n" 														+ \
				u"# of Unmatched (New) Observations (from RIGHT): \t%s\n" % (num_new_obs_from_right) + \
				u"# of Left values OVERWRITTEN in preference of Right: \t%s\n" % (num_overwrite_from_right) + \
				u"\n" 																	+ \
				u"# of Left values EQUAL to Right values [No Change]: \t%s\n" % (num_equal_left_right) + \
				u"\n" 																	+ \
				u"Total Number of FINAL Observations: \t%s\n" % (len(outer)) 					
	
	#-Output Type-#
	if output == 'final':
		# Note: If other data is present, they will retain _x and _y variables
		del outer[left_col]
		del outer[right_col]
			## -> REMOVE <- ##
			# if dominant == 'right':
			# 	del outer['tmp_right_col']
			## ------------ ##
	elif output == 'stages':
		pass
	else:
		raise ValueError("Output type must be `final` or `stages`")	

	#-Parse Verbosity-#
	if verbose: 
		print report
	return outer


def random_sample(df, sample_size = 1000):
	"""
	Return a Random Sample of a Dataframe
	"""
	rows = np.random.choice(df.index.values, sample_size)
	return df.ix[rows]

def change_message(old_idx, recode):
	"""
	Prepare a change message

	Parameters
	----------
	old_idx : set(old index)
	recode 	: dict('FROM' : 'TO')
	"""
	pass
