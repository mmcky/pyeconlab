XLSX Meta Files
---------------

Files
-----

Generated Data Files
--------------------

[1] intertemporal_eiso3n 	
		Description: 	list of all eiso3n codes and how they are used across the years 1962 to 2000	{1}
		md5hash:  		3331242177b82a4972027f25b7f05664

[2] intertemporal_iiso3n 	
		Description: 	list of all iiso3n codes and how they are used across the years 1962 to 2000 	{1}
		md5hash: 		063e34620148c99f59d968fd248c1cb6

[3] intertemporal_sitc4 	
		Description: 	list of all when sitc4 codes are used across the years 1962 to 2000 			{1}
		md5hash: 		357662baf4db691b10b182e2a683adda

[4] importer-iiso3n_intertemporal_countrycode_spells.xlsx 														{2}
		Description: 	Intertemporal CountryCode Spells of Unique iso3n country codes found in the dataset
		md5hash: 		d5d473689b87da17e767c8eb6b63eb26

[5] exporter-eiso3n_intertemporal_countrycode_spells.xlsx 														{2}
		Description: 	Intertemporal CountryCode Spells of Unique iso3n country codes found in the dataset
		md5hash: 		d5d473689b87da17e767c8eb6b63eb26

Manually Edited / Notes
-----------------------

[1] importer-iiso3n_intertemporal_countrycode_adjustments.xlsx 													{2}
		Description: 	Contains Adjustments and Special Cases to get Consistent Country Classifications Over time. 
						[WARNING: Includes Adjustment notes for Splits and Merges - Do not simply replace from {2}]
		md5hash: 		2a7d7a2ae3ee3308a7837eeb914dcffe
		Notes: 			This File Requires MANUAL ADITIONS to Establish Appropriate Groups

[1] exporter-eiso3n_intertemporal_countrycode_adjustments.xlsx 													{2}
		Description: 	Contains Adjustments and Special Cases to get Consistent Country Classifications Over time. 
						[WARNING: Includes Adjustment notes for Splits and Merges - Do not simply replace from {2}]
		md5hash: 		ac11487884239e53d39efb4ecb30983e
		Notes: 			This File Requires MANUAL ADITIONS to Establish Appropriate Groups


Construction Recipe:
--------------------
{1}		from pyeconlab import NBERFeenstraWTFConstructor
		source_dir=r"E:\work-data\x_datasets\36a376e5a01385782112519bddfac85e"
		a = NBERFeenstraWTFConstructor(source_dir=source_dir)
		a.set_dataset(a.raw_data)
		a.write_metadata()

{2} 	from pyeconlab import NBERFeenstraWTFConstructor
		SOURCE_DATA_DIR = "E:\\work-data\\x_datasets\\36a376e5a01385782112519bddfac85e\\" #win7
		a = NBERFeenstraWTFConstructor(source_dir=SOURCE_DATA_DIR)
		a.countries_only()
		i,e = a.intertemporal_countrycodes(dataset=True)
		
		from pyeconlab.util import compute_number_of_spells
		#ispells
		ispells = compute_number_of_spells(i)
		total_coverage = len(ispells.columns)
		ispells['coverage'] = ispells.sum(axis=1)
		ispells['prc_coverage'] = ispells['coverage'] / total_coverage
		ispells.to_excel('importer-iiso3n_intertemporal_countrycode_spells.xlsx')

		ispell_cases = ispells[ispells['coverage'] != total_coverage]
		ispell_cases.to_excel('importer-iiso3n_intertemporal_countrycode_adjustments.xlsx') #Requires Manual Adjustment

		#espells
		espells = compute_number_of_spells(e)
		total_coverage = len(espells.columns)
		espells['coverage'] = espells.sum(axis=1)
		espells['prc_coverage'] = espells['coverage'] / total_coverage
		espells.to_excel('exporter-eiso3n_intertemporal_countrycode_spells.xlsx')

		espell_cases = espells[espells['coverage'] != total_coverage]
		espell_cases.to_excel('exporter-eiso3n_intertemporal_countrycode_adjustments.xlsx') #Requires Manual Adjustment