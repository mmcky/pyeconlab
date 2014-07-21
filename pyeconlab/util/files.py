'''
	Helper OS Functions

	home_folder 		: 	returns the home folder of the current user
'''

# ------- #
# Imports #
# ------- #

import os
import re
import sys

# --------- #
# Utilities #
# --------- #


def expand_homepath(directory):
	''' 
		Expands '~' found in any path
	'''
	if re.match(r'~', directory):
		directory = re.sub(r'~', os.path.expanduser("~"), directory)
	if sys.platform.startswith('win'): 											#Adjustment for Windows for well displayed path
		directory = re.sub(r'/', r'\\', directory)
	return directory

def check_directory(directory, verbose=False):
	"""
	Performs a simple check on an incoming directory format and then makes sure the directory exists
	
	Parameters
	----------
	directory 	: 	string
					a directory string to run checks on

	Returns:
	--------
	directory 	: 	The same or an adjusted directory

	Notes:
	------
	Performs a check for Win7 and adjusts a '/' to a '\\' to keep consistent styling

	Raises:
	-------
	ValueError
		If Directory doesn't exist
	"""
	# Ends with '/'
	if directory[-1] != '/' and directory[-1] != '\\':
		if verbose: print "[WARNING] Directory does not end in a `/`. Checking Adjusted Directory"
		directory = directory + '/'
	# - Adjustment for Windows for well displayed path - #
	if sys.platform.startswith('win'): 											
		directory = re.sub(r'/', r'\\', directory)
	# - Check Directory Exists - #
	if not os.path.isdir(directory):
		raise ValueError("Directory: %s is NOT a valid directory!" % directory) 
	return directory

def home_folder():
	'''
		Return the Home Folder
	'''
	return os.path.expanduser('~')
