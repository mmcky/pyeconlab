"""
SITC Trade Classifications
==========================

This package contains SITC trade classification details. This includes items such as Codes and Names. 
If you are looking for conversion between trade classification tables (i.e. SITCR2-HS2002). 
This information is contained in trade concordance

Data Files:
----------
see data/README.md

Future Work:
-----------
[1] Add Metadata to the SITC objects (i.e. applicable_years, data_available_years etc.)

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

	def __init__(self, revision, source_institution='un', verbose=False):
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
			self.source_web = u"http://unstats.un.org/unsd/tradekb/Knowledgebase/UN-Comtrade-Reference-Tables"
			self.data = pd.read_csv(DATA_PATH + 'un/' + 'S'+str(revision)+'.txt')
		#-Source: World Bank - WITS-#
		elif source_institution == 'wits':
			raise NotImplementedError('wits not yet implemented')
		else:
			raise ValueError("source_institution must be 'un' or 'wits'")
		#-Run Some Standard Methods-#
		self.construct_level()
		self.construct_description()

	def __repr__(self):
		""" Representation String """
		obstring 	= 	"SITC Revision: %s\n" % self.revision 	+\
						"-----------------\n"					+\
						"Level 1 Codes: %s\n" % len(self.L1) 	+\
						"Level 2 Codes: %s\n" % len(self.L2) 	+\
						"Level 3 Codes: %s\n" % len(self.L3) 	+\
						"Level 4 Codes: %s\n" % len(self.L4) 	+\
						"Level 5 Codes: %s\n" % len(self.L5) 	+\
						"\n"									+\
						"Source: %s (%s)" % (self.source_institution, self.source_web)
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

	def get_level(self, level):
		""" Return Level Data based on a specified level """
		if level == 1:
			return self.L1
		elif level == 2:
			return self.L2
		elif level == 3:
			return self.L3
		elif level == 4:
			return self.L4
		elif level == 5:
			return self.L5
		else:
			raise ValueError("[ERROR] Level can only be specifed as 1,2,3,4 or 5!")

	@property 
	def codes(self):
		return self.data['Code']


	#-------------------#
	#-Construct Methods-#
	#-------------------#

	def construct_level(self):
		"""
		Build Level Indicator From the Code Length
		"""
		self.data['level'] = self.data['Code'].apply(lambda x: len(x))

	def construct_description(self):
		"""
		Construct a Full Description from ShortDescription and LongDescription

		Note:
		-----
		[1] Currently this doesn't look necessary. ShortDescription contains enough of the information
		"""
			# def decide_join(sd,ld):
			# 	""" Decide How to Joing ShortDescription and LongDescription """
			# 	if ld[0:2] == '--':
			# 		return sd + ld[2:]
			# 	elif sd == ld:
			# 		return sd
			# 	else:
			# 		raise ValueError("What to do?")
		self.data['Description'] = self.data[['ShortDescription']]

	#---------------#
	#-Other Methods-#
	#---------------#

	def description(self, code):
		""" 
		Return Code Description String
		"""
		return self.data[self.data['Code'] == code]['Description'].values[0] 		


	def code_description_dict(self, level=None):
		""" 
		Return a {Code: Description} Dictionary
		level 	: 	Can be Specified [1,2,3,4, or 5]
					[Default is to return the entire dictionary of ALL levels]
		"""
		if type(level) == int:
			data = self.get_level(level)
			return data[['Code', 'Description']].set_index(['Code'])['Description'].to_dict()
		return self.data[['Code', 'Description']].set_index(['Code'])['Description'].to_dict()
		

#----------#
#-Revision-#
#----------#

def SITCR1():
	"""
	Return an SITC Revision 1 Object
	
	Notes
	-----
	[1] By generating an object we can set attributes that are added by considering the example below.
		Add:
		----
			applicable_years
			data_years
	"""
	sitc = SITC(revision=1)
	# sitc.applicable_years = ???
	return sitc 

def SITCR2():
	"""
	Return an SITC Revision 2 Object
	"""
	return SITC(revision=2)

def SITCR3():
	"""
	Return an SITC Revision 3 Object
	"""
	return SITC(revision=3)

def SITCR4():
	"""
	Return an SITC Revision 4 Object
	"""
	return SITC(revision=4)


