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
import hashlib

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
	directory 	: 	string (a directory string to run checks on)

	Returns:
	--------
	directory 	: 	string (same or adjusted)

	Notes:
	------
	Performs a check for Win7 and adjusts a '/' to a '\\' to keep consistent styling

	Raises:
	-------
	ValueError : If Directory doesn't exist
	"""
	# - Ensure passed text is specified as a directory - #
	if directory[-1] != '/' and directory[-1] != '\\':
		if verbose: print "[WARNING] Directory does not end in a `/` or '\\'."
		directory = directory + '/'
		if verbose: print "Will try: %s" % directory
	# - Adjustment for Windows for well displayed path - #
	if sys.platform.startswith('win'): 											
		directory = re.sub(r'/', r'\\', directory)
	# - Check Directory Exists - #
	if not os.path.isdir(directory):
		raise ValueError("%s is NOT a valid directory" % directory) 
	return directory

def home_folder():
	'''
		Return the Home Folder
	'''
	return os.path.expanduser('~')

def package_folder(__file__, localdir):
	"""
	Simple locator for finding package folders
	
	Parameters
	----------
	__file__ 	: pass in the file location
	localdir 	: specify the directory name 
				  (i.e. 'data' if calling file is in tests/ this will return absolute reference for tests/data)

	Returns
	-------
	path 		: absolute path to package sub-directory

	Notes
	-----
	[1] This only works for local sub-directories (which is the majority of use cases)

	"""
	this_dir, this_filename = os.path.split(__file__)
	path = os.path.join(this_dir, localdir)
	return check_directory(path)

def verify_md5hash(fl, md5hash):
	"""
	Verify a File's md5 hash

	Parameters
	----------
	fl 	: absolute reference to file
	hash : 	md5hash to check against

	Returns
	-------
	True/False
	"""
	computed_md5hash = hashlib.md5(open(fl, 'rb').read()).hexdigest()
	return (md5hash == computed_md5hash)
