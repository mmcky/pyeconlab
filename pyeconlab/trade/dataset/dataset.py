'''
	Dataset Construction Classes

	Datasets:
	--------
		1. Feenstra/NBER Data 
		2. BACI Data
		3. CEPII Data
		4. UNCTAD Revealed Capital,Labour, and Land

	Issues:
	-------
		1. 	How best to Incorporate the Source Dataset files. They can be very large 
			[Currently will pull in from a MyDatasets Object]
		2. 	This will be pretty slow to derive data each time from the raw data and will drive unnecessary wait times
			(i.e. Probably Need NBERPreCompiled and NBER Classes)


	Future Work:
	-----------
		1. How to Handle Custom Altered Made Datasets such as Intertemporally Consistent NBER-BACI Data?
'''

import pandas as pd

######## - IN WORK - ##########

# - Put into Appropriate Dataset Subpackages - #

class BACI(object):
	pass

class CEPII(object):
	pass

