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

	#-Special Cases for use with nber.intertemporal_productcode_lists(return_table=True)-#
	#-Ensure Special Case Encoding is Correct-#
	IC6200SpecialCases = {
		"L4" 	: 	{
			"drop"	: 		[	"0021", "0022", "0023", "0024", "0025", 		\
								"0031", "0035", "0039", 						\
								"9000", "9110", "9310", "9410", "9610", "9710"   #-Ensure Chapter 9 is Dropped-#
							], 	 	
			"collapse" : 	[],
			"keep" 	: 		[], 
		},
		"L3" 	: 	{
			# DROP
			# 002 = Unofficial code that only appears in a few countries 1962 to 1965 shouldn't be merged with 001#
			# 003 = Unofficial code that only appears in a few countries 1962 to 1965 shouldn't be merged with 001#
			"drop"	: 		["002", "003", "911", "931", "941", "961", "971"], 		#-Ensure Chapter 9 is Dropped-#
			"collapse" : 	[],
			"keep" 	: 		[],
		},
		"L2" 	: 	{
			# DROP #
			# At this level it is important to keep the products disaggregated as Chapters contain very different types of products
			"drop"	: 		["60", "70", "80", "90", "91", "93", "94", "96", "97"],
			"collapse" : 	[],	
			"keep" 	: 		["61", "62", "63", "64", "65", "66", "67", "68", "69", 	\
							 "71", "72", "73", "74", "75", "76", "77", "78", "79", 	\
							 "81", "82", "83", "84", "85", "87", "88", "89", 		\
							 "95" 														#Keep Only Armoured Vehicles (Technologically Advanced but very distorted)
							 ],	
		},		
	}

	#-Static Version of the intertemporal_productcode_lists() method NormAvg=1, RowMax=4-#
	#-See meta adjustment files and xlsx/intertemporal_productcoes_sitcl4_drop.csv-#
	IC6200 = {
		#-SITCL4-#
		4 : 	{
			"drop" 		: ["","0010","0021","0022","0023","0024","0025","0031","0035","0039","0110","0120","0220","0222","0231","0581","0710","0720","0750","0810","0901","0910","1120","1220","2110","2200","2220","2321","2330","2400","2470","2480","2610","2630","2650","2660","2680","2710","2770","2780","2829","2920","3200","4110","4200","4230","4240","4310","5100","5120","5130","5140","5150","5330","5500","5540","5711","5800","5986","6000","6110","6214","6255","6291","6292","6350","6410","6420","6500","6529","6561","6585","6610","6620","6640","6659","6661","6710","6726","6735","6742","6750","6762","6820","6840","6850","6860","6870","6890","6900","6930","6956","6963","6995","7000","7100","7121","7147","7164","7165","7189","7200","7231","7232","7240","7265","7266","7285","7300","7311","7313","7314","7315","7316","7317","7331","7351","7359","7400","7425","7427","7437","7447","7473","7478","7482","7500","7526","7710","7724","7725","7730","7800","7820","7830","7843","7862","7900","7916","7935","8000","8215","8400","8438","8458","8513","8517","8721","8722","8730","8746","8747","8810","8820","8850","8900","8913","8920","8940","9000","9110","9310","9410","9610","9710"],
			"collapse" 	: ["0140","0141","0142","0149","0250","0251","0252","0340","0341","0342","0343","0344","0370","0371","0372","0410","0411","0412","0420","0421","0422","0450","0451","0452","0459","0480","0481","0482","0483","0484","0488","0540","0541","0542","0544","0545","0546","0548","0560","0561","0564","0565","0570","0571","0572","0573","0574","0575","0576","0577","0579","0580","0582","0583","0585","0586","0589","0610","0611","0612","0615","0616","0619","0740","0741","0742","1210","1211","1212","1213","2230","2231","2232","2234","2235","2238","2239","2510","2511","2512","2516","2517","2518","2519","2670","2671","2672","2730","2731","2732","2733","2734","2740","2741","2742","2810","2814","2815","2816","2870","2871","2872","2873","2874","2875","2876","2877","2879","2880","2881","2882","2910","2911","2919","3220","3221","3222","3223","3224","3340","3341","3342","3343","3344","3345","3350","3351","3352","3353","3354","3410","3413","3414","3415","5110","5111","5112","5113","5114","5160","5161","5162","5163","5169","5220","5221","5222","5223","5224","5225","5230","5231","5232","5233","5239","5240","5241","5249","5310","5311","5312","5320","5322","5323","5410","5411","5413","5414","5415","5416","5417","5419","5510","5513","5514","5620","5621","5622","5623","5629","5720","5721","5722","5723","5820","5821","5822","5823","5824","5825","5826","5827","5828","5829","5830","5831","5832","5833","5834","5835","5836","5837","5838","5839","5840","5841","5842","5843","5849","5850","5851","5852","5910","5911","5912","5913","5914","5921","5922","5980","5981","5982","5983","5989","6120","6121","6122","6123","6129","6250","6251","6252","6253","6254","6259","6280","6281","6282","6289","6340","6341","6342","6343","6344","6349","6510","6511","6512","6513","6514","6515","6516","6517","6518","6519","6520","6521","6522","6530","6531","6532","6534","6535","6536","6538","6539","6540","6541","6542","6543","6544","6545","6546","6549","6550","6551","6552","6553","6570","6571","6572","6573","6574","6575","6576","6577","6579","6580","6581","6582","6583","6584","6589","6590","6591","6592","6593","6594","6595","6596","6597","6630","6631","6632","6633","6635","6637","6638","6639","6650","6651","6652","6658","6660","6664","6665","6666","6670","6671","6672","6673","6674","6720","6724","6725","6727","6730","6731","6732","6733","6740","6741","6744","6745","6746","6747","6749","6760","6768","6780","6781","6782","6783","6784","6785","6790","6791","6793","6794","6810","6811","6812","6830","6831","6832","6910","6911","6912","6920","6921","6924","6950","6951","6953","6954","6970","6973","6974","6975","6978","6990","6991","6992","6993","6994","6996","6997","6998","6999","7110","7111","7112","7119","7120","7126","7129","7130","7131","7132","7133","7138","7139","7140","7144","7148","7149","7160","7161","7162","7163","7169","7210","7211","7212","7213","7219","7220","7223","7224","7230","7233","7234","7239","7250","7251","7252","7259","7260","7263","7264","7267","7268","7269","7271","7272","7280","7281","7283","7284","7311","7313","7315","7316","7360","7361","7362","7367","7368","7369","7370","7371","7372","7373","7411","7412","7413","7414","7415","7416","7420","7421","7422","7423","7428","7429","7430","7431","7432","7433","7434","7435","7436","7439","7440","7441","7442","7449","7451","7452","7490","7491","7492","7493","7499","7510","7511","7512","7518","7520","7521","7522","7523","7524","7525","7528","7590","7591","7599","7610","7611","7612","7620","7621","7622","7628","7630","7631","7638","7640","7641","7642","7643","7648","7649","7720","7721","7722","7723","7740","7741","7742","7750","7751","7752","7753","7754","7757","7758","7760","7761","7762","7763","7764","7768","7780","7781","7782","7783","7784","7788","7840","7841","7842","7849","7850","7851","7852","7853","7860","7861","7868","7910","7911","7912","7913","7914","7915","7918","7919","7920","7921","7922","7923","7924","7928","7929","7930","7931","7932","7933","7938","8120","8121","8122","8124","8210","8211","8212","8219","8420","8421","8422","8423","8424","8429","8430","8431","8432","8433","8434","8435","8439","8440","8441","8442","8443","8450","8451","8452","8459","8460","8461","8462","8463","8464","8465","8470","8471","8472","8480","8481","8482","8483","8484","8740","8741","8742","8743","8744","8745","8748","8749","8930","8931","8932","8933","8935","8939","8950","8951","8952","8959","8970","8972","8973","8974","8980","8981","8982","8983","8989","8990","8991","8993","8994","8996","8997","8998","8999"],
				},
		#-SITCL3-#
		3 : 	{
			"drop" 		: ["","002","003","090","240","510","550","571","580","600","629","650","670","690","700","730","731","733","735","740","747","748","750","790","800","840","890","891","900","911","931","941","961","971"],
			"collapse" 	: ["220","222","223","320","322","323","420","423","424","710","711","712","713","714","716","718","720","721","722","723","724","725","726","727","728","771","772","773","774","775","776","778","780","781","782","783","784","785","786"],
				},
		#-SITCL2-#
		2 : 	{
			"drop" 		: ["","60","70","80","90","91","93","94","96","97"],
			"collapse" 	: [],
				}
	}

	# IC6200 = OrderedDict(sorted(IC6200.items(), key=lambda t: t[0]))

	#--------------#
	#-1974 to 2000-#
	#--------------#

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
	#-1984 to 2000-#
	#--------------#









	#--------------#
	#----INWORK----#
	#--------------#


	#-Intertemporally Consistent 1962 to 2000: Manually Constructed-#
	# Note: Table Informed by intertemporal_productcode_lists(return_table=True, include_special=True)
	# IC6200Manual = {
	# 	#-SITCL4-#
	# 	"L4" : 	{
	# 		"collapse" 	: [],
	# 		"drop" 		: [],
	# 			},
	# 	#-SITCL3-#
	# 	"L3" : 	{
	# 		#-Collapse-#
	# 		# 675 = Hoop and strip of iron or steel, hot-rolled or cold-rolled (COLLAPSE with 671,2,3,4,6,7,8,9 = Iron and Steel) 
	# 		# 689 = Miscellaneous non-ferrous base metals, employed in metallurgy (Collapse with 681,2,3,4,5,6,7,8 = Various Metals)
	# 		# 716 = Rotating electric plant and parts thereof, nes (Collapse with 711,2,3,4,8 = Engines and Motors)
	# 		# 771 = Electric power machinery, and parts thereof, nes (Collapse with 772,3,4,5,6,8 = Specialist Electronic Equipment)
	# 		# 843 = Womens, girls, infants outerwear, textile, not knitted or crocheted (Collapse with 842,4,5,6,7,8 = Textile and Apparel)
	# 		# 844 = [see above]
	# 		# 845 = [see above]
	# 		# 846 = [see above]
	# 		# 893 = Articles, nes of plastic materials (Collapse with 892,4,5,6,7,8,9 = Misc. Manufactures)
	# 		"collapse" 	: ["67", "68", "71", "74", "75", "77", "84", "89"],
	# 		# 911 = Postal packages not classified according to kind (Not Complete Across Years and Not Collapsable)
	# 		# 971 = Gold, non-monetary (excluding gold ores and concentrates) (Not Complete Across Years and Not Collapsible)
	# 		"drop" 		: ["911", "971"],
	# 			},
	# 	#-SITCL2-#
	# 	"L2" : 	{
	# 		"collapse" 	: 	[],
	# 		"drop" 		: 	[],
	# 			}
	# }


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


