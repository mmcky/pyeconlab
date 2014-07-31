Trade Classification Subpackage Data
====================================

Sources
=======

	un
	--	 	
		http://unstats.un.org/unsd/tradekb/Knowledgebase/UN-Comtrade-Reference-Tables
		http://unstats.un.org/unsd/tradekb/Knowledgebase/Harmonized-Commodity-Description-and-Coding-Systems-HS
		http://unstats.un.org/unsd/tradekb/Knowledgebase/Comtrade-Country-Code-and-Name


	wits
	----
		http://wits.worldbank.org/referencedata.html


Folders
=======

	un/
		S1.txt 				: 	Description: SITC Revision 1 Classifications
								Type:		csv separated text file
								Headers: 	["Code","ShortDescription","LongDescription","isBasicLevel","AggregateLevel","parentCode"]
								Downloaded: 31/07/2014
								md5hash: 	38295f99db5ee8d588411d1c6cc01a1f

		S2.txt 				: 	Description: SITC Revision 2 Classifications
								Type:		csv separated text file
								Headers: 	["Code","ShortDescription","LongDescription","isBasicLevel","AggregateLevel","parentCode"]
								Downloaded: 31/07/2014
								md5hash: 	57709687a9aa8bc9ab45c10ae0eeaf48

		S3.txt 				: 	Description: SITC Revision 3 Classifications
								Type:		csv separated text file
								Headers: 	["Code","ShortDescription","LongDescription","isBasicLevel","AggregateLevel","parentCode"]
								Downloaded: 31/07/2014
								md5hash: 	bb120abdee8c8eb97edde8bf43394a11

		S4.txt 				: 	Description: SITC Revision 4 Classifications
								Type:		csv separated text file
								Headers: 	["Code","ShortDescription","LongDescription","isBasicLevel","AggregateLevel","parentCode"]
								Downloaded: 31/07/2014
								md5hash: 	f53be9c2c7edd12fe2d03c7be09a49ce				

		**Note:** There are other archives: http://unstats.un.org/unsd/tradekb/Knowledgebase/UN-Comtrade-Reference-Tables

	wits/
		SITCProducts.zip 	:	Description: SITC Product Classifications
								Contains: 	SITCPrdoucts.xls (With Sheets: `SITC 1`, `SITC 2`, `SITC 3`, `SITC 4`)
								Type: 		ZIP Archive
								Downloaded: 31/07/2014 
								md5hash: 	8fa873eabaddcd23752ffdb82fbee94f
								Notes: 		[1] Stored in Compressed ZIP file to save space in the repository
											Can I decompress within the project on the fly using zip package?

		**Note:** There are other archives: http://wits.worldbank.org/referencedata.html
