'''
	Init File for trade Subpackage

	Actual Trade Data needs to be referenced when constructing the trade objects


	Subpackage:
	----------
		[1] classification 	=> 	Contains SITC, HS Classification Objects
		[2] concordances 	=> 	Contains Concordance Data (i.e. CountryName -> ISO3C Mappings etc)
		[3] data 			=> 	Data Constructors & Compilers
								[Note: This does NOT contain actual TradeData]
		[4] test 			=> 	Test Suites
	
	Future:
	------
		[#] productspace 	=> 	General Functions Suited to ProductSpace Research [Some of this is integrated into Systems, Networks]
	
	Systems:
	-------
	ProductLevelExportSystem.py 	[Object Structure Based on Pandas DataFrames (Long x Wide)]
	ProductLevelExportNetwork.py 	[Object Structure Based on Networkx]

'''								

#from dataset.NBERFeenstraWTF import NBERFeenstraWTFConstructor, NBERFeenstraWTF