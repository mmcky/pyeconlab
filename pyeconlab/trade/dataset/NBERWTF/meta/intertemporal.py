"""
Dynamic / Intertemporal Considerations for NBER Dataset
=======================================================

This Module contains intertemporal Recodes for the NBER Dataset

Notes
-----
[1] Many of these concordances are HAND constructed by looking at supporting meta data contained in ``xlsx`` etc.

"""

from collections import OrderedDict
from pyeconlab.util import from_dict_to_csv

class IntertemporalCountries(object):
	""" 
	Class Containing Intertemporal / Dynamic Consistent Country Recodes

	Documentation
	-------------
	Hand Constructed - N/A

	Future Work 
	-----------
	[1] Allow Specification of Year Brackets
	[2] Include Documentation to Support these Codings
	
	"""

	#-Joint Importer / Exporter Recodes-#

	#-Contains ISO3C to SPECIAL CODES Required to Make 1962 to 2000 Dynamically Consistent (Strict)-#
	#-Moved '.' recodes to incomplete_iso3c_for_1962_2000-#
	iso3c_for_1962_2000 = {
			'ARM' 	: 'SP1',
			'AZE' 	: 'SP1',
			'BGD' 	: 'SP2',
			'BLR' 	: 'SP1',
			'BIH' 	: 'SP3',
			'MAC' 	: 'CHN', 	#Merge Macao with China
			'HRV' 	: 'SP3',
			'CZE' 	: 'SP4',
			'CSK'	: 'SP4',
			'EST' 	: 'SP1',
			'DDR' 	: 'SP5',
			'DEU'	: 'SP5',
			'SUN' 	: 'SP1',
			'YEM' 	: 'SP6',
			'YMD' 	: 'SP6', 
			'YUG' 	: 'SP3',
			'GEO'	: 'SP1',
			'KAZ' 	: 'SP1',
			'KGZ'	: 'SP1',
			'LVA' 	: 'SP1',
			'LTU' 	: 'SP1',
			'MDA' 	: 'SP1',
			'RUS' 	: 'SP1',
			'SVK' 	: 'SP4',
			'SVN' 	: 'SP3',
			'MKD' 	: 'SP3',
			'TJK'	: 'SP1',
			'TKM' 	: 'SP1',
			'UKR' 	: 'SP1',
			'UZB' 	: 'SP1',
			'SCG' 	: 'SP3',
	}


	iso3c_for_1962_2000_definitions = {
			#-Splits-#
			'SP1' 	: 	('SUN', ['ARM', 'AZE', 'BLR', 'EST', 'GEO', 'KAZ', 'KGZ', 'LVA', 'LTU', 'MDA', 'RUS', 'TJK', 'TKM', 'UKR', 'UZB']),
			'SP2' 	: 	('IND', ['IND', 'BGD']),
			'SP3' 	: 	('YUG', ['BIH', 'HRV', 'MKD', 'MNE', 'SVN', 'SRB']),
			'SP4' 	: 	('CSK', ['CZE', 'SVK']),
			#-Joins-#
			'SP5' 	: 	(['DEU','DDR'], 'DEU'), 		
			'SP6' 	: 	(['YEM', 'YMD'], 'YEM'), 		
	}

	incomplete_iso3c_for_1962_2000 = {
			'ARE' 	: '.', 		#INTERPOLATE?
			'BLZ'	: '.', 		#INTERPOLATE?
			'FLK' 	: '.',
			'GIB' 	: '.', 		#INTERPOLATE?
			'GRL' 	: '.', 		#INTERPOLATE?
			'MWI'	: '.',		#INTERPOLATE?
			'PSE' 	: '.',
			'RWA' 	: '.', 		#INTERPOLATE?
			'SYC' 	: '.', 		#Add to FRA?
			'SHN' 	: '.', 		#Merge with Britain?
			'KNA' 	: '.', 		#INTERPOLATE?
			'ZWE' 	: '.', 		#INTERPOLATE?
	}

	def iso3c_for_1962_2000_csv(self, fl='intertemporal_iso3c_for_1962_2000.csv', target_dir='csv/'):
		"""
		Simple Utility for writing iso3c_for_1962_2000 to csv file
		"""
		from_dict_to_csv(self.iso3c_for_1962_2000, header=['iso3c', '_recode_'], fl=fl, target_dir=target_dir)

	def incomplete_iso3c_for_1962_2000_csv(self, fl='incomplete_iso3c_for_1962_2000.csv', target_dir='csv/'):
		"""
		Simple Utility for writing incomplete_iso3c_for_1962_2000 to csv file
		"""
		from_dict_to_csv(self.incomplete_iso3c_for_1962_2000, header=['iso3c', '_recode_'], fl=fl, target_dir=target_dir)


class IntertemporalProducts(object):
	""" 
	Class Containing Intertemporal / Dynamic Consistent Product Recodes

	Definitions
	-----------
	"IC6200" - Intertemporally Consistent 1962 to 2000
	"IC7400" - Intertemporally Consistent 1974 to 2000

	Documentation 
	-------------
	intertemporal_sitc4_wmeta_adjustments.xlsx
	intertemporal_sitc3_wmeta_adjustments.xlsx
	intertemporal_sitc2_wmeta_adjustments.xlsx

	Additional Supporting Documentation found in xlsx/

	"""

	#-Intertemporally Consistent 1962 to 2000-#
	IC6200 = {
		#-SITCL4-#
		"L4" : 	{
			"collapse" 	: [],
			"drop" 		: [],
				},
		#-SITCL3-#
		"L3" : 	{
			#-Collapse-#
			# 675 = Hoop and strip of iron or steel, hot-rolled or cold-rolled (COLLAPSE with 671,2,3,4,6,7,8,9 = Iron and Steel) 
			# 689 = Miscellaneous non-ferrous base metals, employed in metallurgy (Collapse with 681,2,3,4,5,6,7,8 = Various Metals)
			# 716 = Rotating electric plant and parts thereof, nes (Collapse with 711,2,3,4,8 = Engines and Motors)
			# 771 = Electric power machinery, and parts thereof, nes (Collapse with 772,3,4,5,6,8 = Specialist Electronic Equipment)
			# 843 = Womens, girls, infants outerwear, textile, not knitted or crocheted (Collapse with 842,4,5,6,7,8 = Textile and Apparel)
			# 844 = [see above]
			# 845 = [see above]
			# 846 = [see above]
			# 893 = Articles, nes of plastic materials (Collapse with 892,4,5,6,7,8,9 = Misc. Manufactures)
			"collapse" 	: ["67", "68", "71", "74", "75", "77", "84", "89"],
			# 911 = Postal packages not classified according to kind (Not Complete Across Years and Not Collapsable)
			# 971 = Gold, non-monetary (excluding gold ores and concentrates) (Not Complete Across Years and Not Collapsible)
			"drop" 		: ["911", "971"],
				},
		#-SITCL2-#
		"L2" : 	{
			"collapse" 	: 	[],
			"drop" 		: 	[],
				}
	}

	# IC6200 = OrderedDict(sorted(IC6200.items(), key=lambda t: t[0]))

	#-Intertemporally Consistent 1974 to 2000-#
	IC7400 = {
		#-SITCL4-#
		"L4" : 	{
			"collapse" 	: [],
			"drop" 		: [],
				},
		#-SITCL3-#
		#Note: Nothing Required as Post 1974 Items are Consistent
		"L3" : 	{
			"collapse" 	: [],
			"drop" 		: [],
				},
		#-SITCL2-#
		"L2" : 	{
			"collapse" 	: 	[],
			"drop" 		: 	[],
				}
	}

	# IC7400 = OrderedDict(sorted(IC7400.items(), key=lambda t: t[0]))












	#--------------#
	#----INWORK----#
	#--------------#


	#-SAME AS ABOVE except "countryname" to SPECIAL CODES Required to Make 1962 to 2000 Dynamically Consistent-#
	
	# countryname_for_1962_2000 = { 
		
	# 	# - WORKING HERE - # 
	
	# }

	# #-Exporter Specific-#
	# #-------------------#

	# exporter_recodes_for_1962_2000 = {
	# 		'ARM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'AZE' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'BGD' 	: 'IND-INDBGD',
	# 		'BLR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'BLZ'	: '.', 														#INTERPOLATE?
	# 		'BIH' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'MAC' 	: 'CHN', 													#Merge Macao with China
	# 		'HRV' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'CZE' 	: 'CSK-CZESVK',
	# 		'CSK'	: 'CSK-CZESVK',
	# 		'EST' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'FLK' 	: '.',
	# 		'DDR' 	: 'DEU-DDRDEU',
	# 		'DEU'	: 'DEU-DDRDEU',
	# 		'SUN' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'YEM' 	: 'YEMYMD-YEM',
	# 		'YMD' 	: 'YEMYMD-YEM', 
	# 		'YUG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'GEO'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'GIB' 	: '.', 														#INTERPOLATE?
	# 		'GRL' 	: '.', 														#INTERPOLATE?
	# 		'KAZ' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'KGZ'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'LVA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'LTU' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'MWI'	: '.',														#INTERPOLATE?
	# 		'PSE' 	: '.',
	# 		'MDA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'RUS' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'RWA' 	: '.', 														#INTERPOLATE?
	# 		'SYC' 	: '.', 														#Add to FRA?
	# 		'SVK' 	: 'CSK-CZESVK',
	# 		'SVN' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'SHN' 	: '.', 														#Merge with Britain?
	# 		'KNA' 	: '.', 														#INTERPOLATE?
	# 		'MKD' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'TJK'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'TKM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'UKR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'ARE' 	: '.', 														#INTERPOLATE?
	# 		'UZB' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
	# 		'SCG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
	# 		'ZWE' 	: '.', 														#INTERPOLATE?
	# }

	# #-Importer Specific-#
	# #-------------------#

	# importer_recodes_for_1962_2000 = {
		
	# 	# - WORKING HERE - #
	
	# }


