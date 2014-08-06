XLSX Meta Files
---------------

Files
-----
[1] intertemporal_eiso3n 	
		Description: 	list of all eiso3n codes and how they are used across the years 1962 to 2000	{1}
		md5hash:  		3331242177b82a4972027f25b7f05664
[2] intertemporal_iiso3n 	
		Description: 	list of all iiso3n codes and how they are used across the years 1962 to 2000 	{1}
		md5hash: 		063e34620148c99f59d968fd248c1cb6
[3] intertemporal_sitc4 	
		Description: 	list of all when sitc4 codes are used across the years 1962 to 2000 			{1}
		md5hash: 		357662baf4db691b10b182e2a683adda


Construction Recipe:
--------------------
{1}		from pyeconlab import NBERFeenstraWTFConstructor
		source_dir=r"E:\work-data\x_datasets\36a376e5a01385782112519bddfac85e"
		a = NBERFeenstraWTFConstructor(source_dir=source_dir)
		a.set_dataset(a.raw_data)
		a.write_metadata()