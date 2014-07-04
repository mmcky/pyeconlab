PyEconLab 
===========

Python Economics Laboratory
---------------------------

This package contains methods and routines for conducting research with a primary focus on the field of Economics. The current primary focus is on trade and most develpment is occuring in the trade supackage. However in the future other subpackages can be added as research agenda develops. 

Usage
-----

	from pyeconlab.trade import CountryLevelExportSystem
	c = CountryLevelExportSystem(source_dir='data/', fl='somedata.csv')
	c.countries
	... etc


Organisation
------------

The basic organisation of the project is:

	/pyecontrade
		/test 							Tests for Package
		
		/trade 							Subpackage: International Trade
			/classification 			Subpackage: Classifications of Trade Data: HS, SITC
				/data
					*.meta 				Meta Data of Data
					*.csv	
				__init__.py
				classification.py
			/concordance 				Subpackage: Concordances and Correlation Tables
				/data
					*.meta 				Meta Data of Data
					*.csv	
				__init__.py
				concordance.py
			/dataset     	 			DataSet Constructors & Compilation from RAW data		
				DataConstructors.py 	-> Convert /raw files into DataSets
				Datasets.py 			-> Cleaned Dataset Objects
				
				?? - OR - ??
				
				/compile
					DataConstructor.py
				Datasets.py
	
			/test						Tests for SubModule
			
			__init.py
			CountryLevelExportSystem.py
			CountryLevelExportNetwork.py
			ProductLevelExportSystem.py
			ProductLevelExportNetwork.py

		?? - FUTURE -??

			/cplevel 						Country, Product Level Trade Systems
				ProductLevelExportSystem.py
				ProductLevelExportNetwork.py
				... etc
			/clevel 						Country Level Trade Systems
				CountryLevelExportSystem.py
				CountryLevelExportNetwork.py

		/wdi
			/data
			__init__.py
			WDI.py
		__init__.py
		setup.py
		README.md

Data
----

This project only currently supports RAW data that resides outside of the package (due to the large size of most datasets)however data such as Concordances & Aggregations are included (typically found in the relevant subpackage as a csv file). Data files should be encoded in (.csv) to be tool neutral, relatively efficient, and simple!