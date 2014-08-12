"""
DataFrame Utilities

Organisation
------------
[1] Index Functions
[2] Merge Functions 
[3] Row Finding Functions
[4] Sampling Functions
[5] Attribute Functions
[6] Assert Functions
[7] Intertemporal/Dynamic Functions
---
[Z] Staging Area

Future Work
-----------
[1] Split this file into different function types: dataframe_index.py, dataframe_merge.py etc.

"""

import copy
import re
import pandas as pd
import numpy as np
from itertools import chain, repeat

# ------------------- #
# - Index Functions - #
# ------------------- #

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

# ----------------- #
# - Merge Functions - #
# ----------------- #


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
	[2] Write Tests
	[3] This could be rewritten to make use of pandas.combine() to combine dataframes. Would be better tested

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
	report = 	u"MERGE Report [Rule: %s, LEFT: %s, RIGHT: %s]\n" % (dominant, left_col, right_col) + \
				u"------------\n" 														+ \
				u"# of Left Observations: \t%s\n" % (num_ldf) 							+ \
				u"# of Right Observations: \t%s\n" % (num_rdf) 							+ \
				u"  `ON` Matched Observations: \t%s\n" % (num_matched) 					+ \
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





# ------------------------- #
# - Row Finding Functions - #
# ------------------------- #

def find_row(df, row):
	"""
	Find and Return a Row in a DataFrame

	[1] This needs testing 
	"""
	for col in df:
		df = df.loc[(df[col] == row[col]) | (df[col].isnull() & pd.isnull(row[col]))]
	return df





# ---------------------- #
# - Sampling Functions - #
# ---------------------- #

def random_sample(df, sample_size = 1000):
	"""
	Return a Random Sample of a Dataframe
	"""
	rows = np.random.choice(df.index.values, sample_size)
	return df.ix[rows]






# ----------------------- #
# - Attribute Functions - #
# ----------------------- #

# pd.DataFrame.operations = placeholder for attaching op_strings

def update_operations(df, add_op_string):
	""" Update a Special operations attribute on a DataFrame """
	try:
		if type(df.operations) == str or type(df.operations) == unicode:
			df.operations += add_op_string
	except:
		df.operations = add_op_string
	# return df


def check_operations(df, op_string, verbose=False):
	""" Check if operation has been conducted on a DataFrame with re.search(op, df.operation) """
	try:
		if verbose: print "Searching for %s in %s" % (op_string, df.operations)
		if re.search(op_string, df.operations):
			if verbose: print "[INFO] Operation %s has already been conducted on dataset" % (op_string)
			return True
		else:
			return False
	except:
		return False





# ------------------ #
# - Assert Functions - #
# ------------------ #

def assert_unique_row_in_df(df, row):
	"""
	Assert a Unique Row in DataFrame
	"""	
	assert len(find_row(df, row)) == 1, "Row (%s) Not Found in DataFrame OR has multiple matches (try utils.find_row())" % row

def assert_row_in_df(df, row):
	"""
	Assert Row is found in DataFrame 
	"""
	assert len(find_row(df, row)) >= 1, "Row (%s) Not Found in Dataset" % row

def assert_unique_rows_in_df(df, rows):
	"""
	Assert All Unique Rows in a Dataframe of Rows in the DataFrame
	"""
	for idx, row in rows.iterrows():
		assert_unique_row_in_df(df, row)

def assert_rows_in_df(df, rows):
	"""
	Assert All Rows are found in the DataFrame 
	"""
	for idx, row in rows.iterrows():
		assert_row_in_df(df, row)

# - Examples of Different Ways to Impliment - #
# ------------------------------------------- #

def check_rows_from_random_sample_byduplicated(df, rs):
	"""
	Iterate over a Random Sample to Make Sure the row is contained in the DataFrame
	Approach: Using Duplicated()

	Notes:
	------
	[1] timeit: 9.39 s per loop [Same Data as Other check_rows*] 
	"""
	#-Check Duplicates Initial Condition-#
	if len(df[df.duplicated()]) != 0:
		raise ValueError("[ERROR] Dataset Already Contains Duplicate Rows!")
	for idx, row in rs.iterrows():
		#-Check if Row is in Data-#
		tmp = df.append(row)
		assert len(tmp[tmp.duplicated()]) == 1, "A duplicate row wasn't found for %s" % (row)

def check_rows_from_random_sample_byiterating(df, rs):
	"""
	Iterate over a Random Sample to Make Sure the row is contained in the DataFrame
	Iterating and using equal()

	STATUS: [NOT-WORKING] 
			Equality in the presence of NaN is not established. Using .equal() should account for this

	Notes:
	------
	[1] timeit: N/A [Same Data as Other check_rows*] 
	"""
	match = False
	for rsidx, rsrow in rs.iterrows():
		for idx, s in df.iterrows():
			if s.equals(rsrow):
				match = True
				break
		assert match == True, "Iterating didn't find an equal row %s in the dataframe" % (rsrow)

def check_rows_from_random_sample_byfiltering(df, rs):
	"""
	Iterate over a Random Sample to Make Sure the row is contained in the DataFrame
	Filtering Approach

	Notes:
	------
	[1] timeit: 1.72 s per loop [Same Data as Other check_rows*] 
	"""
	for rsidx, rsrow in rs.iterrows():
		tmp = df
		for idx, val in rsrow.iteritems():
			try:
				if np.isnan(val):
					continue
			except:
				pass
			tmp = tmp[tmp[idx] == val]
		assert len(tmp) == 1, "Filtering didn't produce a unique line in the dataframe: %s" % (len(tmp))

def check_rows_from_random_sample_bybroadcasting(df, rs):
	"""
	Brodcast over a DataFrame Looking for rows in DataFrame

	Notes:
	------
	[1] timeit: 4.14 s per loop [Same Data as Other check_rows*] 
	"""
	for rsidx, rsrow in rs.iterrows():
		assert len(df[((df == rsrow) | (df.isnull() & rsrow.isnull())).all(1)]) == 1

def check_rows_from_random_sample_bybroadcasting_columniteration(df, rs):
	"""
	Broadcast and Iterate Over Columns (Smaller Dimension) due to long data relative to width

	Notes:
	------
	[1] timeit: 1.63 s per loop [Same Data as Other check_rows*]
	[2] This is the fastest implementation and is used in assert_functions 
	"""
	def finder(df, row):
		for col in df:
			df = df.loc[(df[col] == row[col]) | (df[col].isnull() & pd.isnull(row[col]))]
		return df
	
	for rsidx, rsrow in rs.iterrows():
		assert len(finder(df, rsrow)) == 1




# ----------------------------------- #
# - Intertemporal/Dynamic Functions - #
# ----------------------------------- #

def compute_number_of_spells(wide_df, inplace=False):
	"""
	Compute Number of Spells in a Wide DataFrame for Each Row
	Columns : Time Data
	"""
	def num_spells(x):
		""" Compute the spells in each row """
		t = list(x.dropna().unique())
		r = []
		for el in x:
			if not np.isnan(el):				
				r.append(t.index(el)+1)
			else:
				r.append(np.nan) 			#Handle np.nan case
		return r
	#-Options-#
	if not inplace:
		wide_df = wide_df.copy(deep=True)
	#-Core-#
	wide_df = wide_df.apply(num_spells, axis=1)
	return wide_df

def compute_spell_lengths(wide_df, incremental=False, inplace=False):
	"""
	Compute Spell Lengths for Wide DataFrames
	Columns : Time Data

	Usage
	-----
	[1] Useful for computing dynamic or intertemporal data in computing length of spells across years in a wide dataframe
	
	Future Work
	-----------
	[1] Add Tests
	"""
	def spell_len(s):
		spell = 1
		for idx, item in s.iteritems():
			next_idx = idx+1
			if next_idx > s.index[-1]:
				s[idx] = spell
				break
			s[idx] = spell
			if np.isnan(item):
				spell = 1
				s[idx] = np.nan
			elif item == s[next_idx]:
				spell += 1
			else:
				spell = 1
		return s

	def rewrite_group(s, group, group_items):
		for gidx in group:
			s[gidx] = max(group_items)

	def final_len(s):
		group = []
		group_items = []
		for idx, item in s.iteritems():
			next_idx = idx+1
			group.append(idx)
			group_items.append(item)
			if next_idx > s.index[-1]:	
				rewrite_group(s, group, group_items)
				break
			if s[next_idx] > item:
				continue
			else:
				#-Rewrite Max Value for Group-#
				rewrite_group(s, group, group_items)
				group = []
				group_items = []
		return s

	#-Options-#
	if not inplace:
		wide_df = wide_df.copy(deep=True)
	#-Core-#
	wide_df = wide_df.apply(spell_len, axis=1)
	if incremental:
		return wide_df
	wide_df = wide_df.apply(final_len, axis=1)
	return wide_df



def compute_number_of_continuous_spells(wide_df, inplace=False):
	"""
	Compute Number of Continuous Spells in a Wide DataFrame for Each Row
	Columns : Time Data

	This function needs to account for non-adjacent np.nan occurances to compute the number of continuous spells. 
	Perhaps parsing each row and adjusting np.nan() occurances to be [-1, -1, val, -2, ... -n etc.] for [np.nan, np.nan, 4, np.nan,]
	This could be done using compute_spell_lengths?

	Future Work
	-----------
	[1] Add Tests
	"""
	raise NotImplementedError




# ----------- #
# - IN WORK - #
# ----------- #




def change_message(old_idx, recode):
	"""
	Prepare a change message

	Parameters
	----------
	old_idx : set(old index)
	recode 	: dict('FROM' : 'TO')
	"""
	pass
