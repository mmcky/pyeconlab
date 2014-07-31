"""
SITC Trade Classifications
==========================

This package contains SITC trade classification details. This includes items such as Codes and Names. 
If you are looking for conversion between trade classification tables (i.e. SITCR2-HS2002). 
This information is contained in trade concordance

Data Files:
----------
see data/README.md

"""

import os
import pandas as pd

from pyeconlab.util import check_directory

# - Data in data/ - #
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = check_directory(os.path.join(this_dir, "data"))

class SITC(object):
	"""
	SITC Object
	"""
	def __init__(self, revision, source_institution='un'):
		"""
		Load SITC Classification Data
		
		Arguments
		---------
		revision 			: 	[1,2,3,4] 		[SITC Revision Number]
		source_institution 	:	['un', 'wits'] 	[Default: 'un']
								See data/README.md for more information

		"""
		#-Attributes-@
		self.revision 			= revision
		self.source_institution = source_institution

		#-Source: United Nations-#
		if source_institution == 'un':
			self.data = pd.read_csv(DATA_PATH + 'un/' + 'S'+str(revision)+'.txt')
		#-Source: World Bank - WITS-#
		elif source_institution == 'wits':
			raise NotImplementedError('wits not yet implemented')
		else:
			raise ValueError("source_institution must be 'un' or 'wits'")

	def __repr__(self):
		""" Representation String """
		obstring 	= 	"SITC Revision: %s\n" % self.revision
		return obstring

	#------------#
	#-Properties-#
	#------------#

	@property 
	def L1(self):
		return self.data[self.data['level'] == 1]

	@property 
	def L2(self):
		return self.data[self.data['level'] == 2]

	@property 
	def L3(self):
		return self.data[self.data['level'] == 3]

	@property 
	def L4(self):
		return self.data[self.data['level'] == 4]

	@property 
	def L5(self):
		return self.data[self.data['level'] == 5]

	@property 
	def codes(self):
		return self.data['Code']


	#---------#
	#-Methods-#
	#---------#

	def level(self):
		"""
		Build Level Indicator From the Code Length
		"""
		self.data['level'] = self.data['Code'].apply(lambda x: len(x))

	def description(self, code):
		""" 
		Return Code Description
		"""
		
		#- WORKING HERE -#

		return self.data[self.data['Code'] == code]['ShortDescription'] 		#Note this currenlty returns an observation number

	def long_description(self, code):
		"""
		Return Long Description
		"""

		#- WORKING HERE -#

		raise NotImplementedError
		return self.data[self.data['Code'] == code]['ShortDescription'] + ' ' + self.data[self.data['Code'] == code]['LongDescription'] #Note this currenlty returns an observation number


#----------#
#-Revision-#
#----------#

class SITCR2(SITC):
	"""
	SITC Revision 2 Object

	Expands the Available Meta Data Available
	"""
	pass
	
