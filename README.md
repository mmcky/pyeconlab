PyEconLab (Python Economics Laboratory)
======================================

This package contains methods and routines for conducting research with a primary focus on the field of Economics. My primary focus is on trade. However in the future other subpackages can be added as research agenda develops. 

**Author:** Matthew McKay

**Email:** mamckay@gmail.com


Organisation
------------

Need to support data that resides outside of the package however data such as Concordances & Aggregations are included. Data files should be encoded in (.csv) to be tool neutral, relatively efficient, and simple!

	/pyecontrade
		/test 							Tests for Package
		/trade
			/classification
				/data
					*.meta 				Meta Data of Data
					*.csv	
				__init__.py
				classification.py
			/concordance
				/data
					*.meta 				Meta Data of Data
					*.csv	
				__init__.py
				concordance.py
			/dataset     	 			DataSet Constructors & Compilation			
				DataConstructors.py 	-> Convert /raw files into DataSets
				Datasets.py 			-> Cleaned Dataset Objects
				**OR**
				/compile
					DataConstructor.py
				Datasets.py
			/test						Tests for SubModule
			ProductLevelExportSystem.py
			ProductLevelExportNetwork.py
			... etc
		/wdi
			/data
			__init__.py
			WDI.py
		__init__.py
		setup.py
		README.md




