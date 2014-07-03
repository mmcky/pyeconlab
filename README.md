PyEconLab (Python Economics Laboratory)
======================================

This package contains methods and routines for conducting research with a primary focus on the field of Economics. 

Author: Matthew McKay
Email: mamckay@gmail.com

Organisation
------------

Need to support data that resides outside of the package

/trade
	/data     	 				[Trade Specific Data]				
		/raw 					[.gitignore]
		/pickles				[.gitignore]
		/hd5					[.gitignore]
		DataConstructors.py 	-> Convert /raw files into DataSets
		Datasets.py 			-> Useful Datasets (i.e. PennWorldTables, WDI etc)

OR 

/data 					[Useful Economic Data, WDI, PennWorldTables etc]
	/raw
  	data constructors (Converting Raw Data Files into Data Objects)

