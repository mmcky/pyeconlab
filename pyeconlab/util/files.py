'''
	Helper OS Functions
'''

import os

def home_folder():
	'''
		Return the Home Folder

		Note: This currently doesn't work! Why?
	'''
	home_dir = os.path.expanduser('~')
	return home_dir