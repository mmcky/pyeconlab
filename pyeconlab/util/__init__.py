'''
	Subpackage: Utilities
'''

from .convert 	import 	from_series_to_pyfile  	#This allows pyeconlab.util.from_series_to_pyfile()
from .files 	import 	home_folder, check_directory, package_folder, verify_md5hash, expand_homepath
from .dataframe import 	recode_index, random_sample, merge_columns, update_operations, check_operations, 					\
						find_row, assert_unique_row_in_df, assert_row_in_df, assert_unique_rows_in_df, assert_rows_in_df