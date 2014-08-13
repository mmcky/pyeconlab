"""
NBERFeenstraWTF Recodes Meta Data
=================================

This Module contains custom recodes for NBERFeenstraWTF Dataset

Notes
-----
[1] Many of these concordances are HAND constructed by looking at supporting meta data contained in ``xlsx`` etc.

"""


#-----------------------#
#-Intertemporal Recodes-#
#-----------------------#

class intertemporal(object):
	""" 
	Class Containing Intertemporal / Dynamic Consistent Recodes

	Notes
	-----
	[1] Is this the best recoding scheme? It will make plotting quite difficult
	"""

	#-Joint Importer / Exporter Recodes-#
	#-----------------------------------#

	#-Contains ISO3C to SPECIAL CODES Required to Make 1962 to 2000 Dynamically Consistent-#
	iso3c_for_1962_2000 = {
			'ARM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'AZE' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'BGD' 	: 'IND-INDBGD',
			'BLR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'BLZ'	: '.', 														#INTERPOLATE?
			'BIH' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'MAC' 	: 'CHN', 													#Merge Macao with China
			'HRV' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'CZE' 	: 'CSK-CZESVK',
			'CSK'	: 'CSK-CZESVK',
			'EST' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'FLK' 	: '.',
			'DDR' 	: 'DEU-DDRDEU',
			'DEU'	: 'DEU-DDRDEU',
			'SUN' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'YEM' 	: 'YEMYMD-YEM',
			'YMD' 	: 'YEMYMD-YEM', 
			'YUG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'GEO'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'GIB' 	: '.', 														#INTERPOLATE?
			'GRL' 	: '.', 														#INTERPOLATE?
			'KAZ' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'KGZ'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'LVA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'LTU' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'MWI'	: '.',														#INTERPOLATE?
			'PSE' 	: '.',
			'MDA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'RUS' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'RWA' 	: '.', 														#INTERPOLATE?
			'SYC' 	: '.', 														#Add to FRA?
			'SVK' 	: 'CSK-CZESVK',
			'SVN' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'SHN' 	: '.', 														#Merge with Britain?
			'KNA' 	: '.', 														#INTERPOLATE?
			'MKD' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'TJK'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'TKM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'UKR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'ARE' 	: '.', 														#INTERPOLATE?
			'UZB' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'SCG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'ZWE' 	: '.', 														#INTERPOLATE?
	}

	#-SAME AS ABOVE except countryname to SPECIAL CODES Required to Make 1962 to 2000 Dynamically Consistent-#
	countryname_for_1962_2000 = { 
		
		# - WORKING HERE - # 
	
	}

	#-Exporter Specific-#
	#-------------------#

	exporter_recodes_for_1962_2000 = {
			'ARM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'AZE' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'BGD' 	: 'IND-INDBGD',
			'BLR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'BLZ'	: '.', 														#INTERPOLATE?
			'BIH' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'MAC' 	: 'CHN', 													#Merge Macao with China
			'HRV' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'CZE' 	: 'CSK-CZESVK',
			'CSK'	: 'CSK-CZESVK',
			'EST' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'FLK' 	: '.',
			'DDR' 	: 'DEU-DDRDEU',
			'DEU'	: 'DEU-DDRDEU',
			'SUN' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'YEM' 	: 'YEMYMD-YEM',
			'YMD' 	: 'YEMYMD-YEM', 
			'YUG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'GEO'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'GIB' 	: '.', 														#INTERPOLATE?
			'GRL' 	: '.', 														#INTERPOLATE?
			'KAZ' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'KGZ'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'LVA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'LTU' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'MWI'	: '.',														#INTERPOLATE?
			'PSE' 	: '.',
			'MDA' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'RUS' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'RWA' 	: '.', 														#INTERPOLATE?
			'SYC' 	: '.', 														#Add to FRA?
			'SVK' 	: 'CSK-CZESVK',
			'SVN' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'SHN' 	: '.', 														#Merge with Britain?
			'KNA' 	: '.', 														#INTERPOLATE?
			'MKD' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'TJK'	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'TKM' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'UKR' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'ARE' 	: '.', 														#INTERPOLATE?
			'UZB' 	: 'SUN-ARMAZEBLRESTGEOKAZKGZLVALTUMDARUSTJKTKMUKRUZB',
			'SCG' 	: 'YUG-BIHHRVMKDMNESVNSRB',
			'ZWE' 	: '.', 														#INTERPOLATE?
	}

	#-Importer Specific-#
	#-------------------#

	exporter_recodes_for_1962_2000 = {
		
		# - WORKING HERE - #
	
	}