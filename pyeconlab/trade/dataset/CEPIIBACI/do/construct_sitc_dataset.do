*** --------------------------------------------------------------------***
*** Generate Basic SITC Datasets for PyEconLab (CEPII DATA) HS96 	***
*** --------------------------------------------------------------------***

*** Notes
*** -----
*** [1] Currently this requires MANUAL adjustment for directories based on REPO Locations etc
*** [2] Manually set the appropriate flags to produce Datasets A

*** Future Work
*** -----------
*** 1. Add in a level option

set more off 
//set trace on
//set tracedepth 1
 
di "Loading settings for environment: " c(os)

if c(os) == "MacOSX" | c(os) == "Unix" {
	// Sources //
	global SOURCE="~/work-data/datasets/e988b6544563675492b59f397a8cb6bb"
	global META = "~/repos/pyeconlab/pyeconlab/trade/dataset/CEPIIBACI/meta" 				//Hard Coded For Now
	global METACLASS = "~/repos/pyeconlab/pyeconlab/trade/classification/meta" 				//Hard Coded For Now
	// Targets //
	global WORKINGDIR="~/work-temp"
}

if c(os) == "Windows" {
	global SOURCE="D:\work-data\datasets\e988b6544563675492b59f397a8cb6bb"
	global META = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\dataset\CEPIIBACI\meta" 		//Hard Coded For Now
	global METACLASS = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\classification\meta" 	//Hard Coded For Now
	// Targets //
	global WORKINGDIR="D:/work-temp"
}

cd $WORKINGDIR

** Datasets 
** --------
** A: check_concordance=True; adjust_units= False; concordance_institution='un'

** Settings **
global DATASETS "A"

foreach item of global DATASETS {
	
	global DATASET="`item'"
	//global DATASET = "A"
	
	capture log close
	local fl = "cepiibaci_stata_sitcl3_data_"+"$DATASET"+".log"
	log using `fl', replace

	global SETUP_CACHE 0

	di "Processing Option: $DATASET"
	
	if "$DATASET" == "A" {
		global check_concordance = 1
		global adjust_units = 0
	}
	else {
		di "Option %DATASET not valid"
		exit
	}


	** ------------------ ** 
	** Write Concordances **
	** ------------------ ** 
	 
	**Concord to ISO3C**
	**/meta/csv/countrycodes_to_iso3c.csv contains this listing**
	**Copied: 27-08-2014
	**Note: This is not intertemporally consistent**
	insheet using "$SOURCE/country_code_baci96_adjust.csv", clear names
	keep iso3 i
	rename iso3 eiso3c
	order i eiso3c
	save "i_to_eiso3c.dta", replace
	insheet using "$SOURCE/country_code_baci96_adjust.csv", clear names
	keep iso3 i
	rename i j
	rename iso3 iiso3c
	order j iiso3c
	save "j_to_iiso3c.dta", replace

	**Concord to SITC Revision 2 Level 2 Codes**
	**classification/meta/SITC-R2-L3-codes.csv contains this listing**
	**Source: UN
	**Copied: 28-08-2014
	infix using "$METACLASS/SITC-R2-L3-codes.dct", using("$METACLASS/SITC-R2-L3-codes.csv") clear
	save "SITC-R2-L3-codes.dta", replace

	** ----------------- **
	** Convert RAW Files **
	** ----------------- **
	if $SETUP_CACHE == 1 {
		foreach year of num 1998(1)2012 {
			insheet using "$SOURCE/baci96_`year'.csv", clear names
			tostring(hs6), replace
			gen fixleadingzero = 6 - length(hs6)
			codebook fixleadingzero
			replace hs6 = "0"+hs6 if fixleadingzero == 1
			save "$SOURCE/cache/baci96_`year'.dta", replace
		}
	}

	*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **
	 
	 
	******************************************
	**Dataset #1: Bilateral TRADE Data 	**
	******************************************

	** WORKING HERE **

	// Compile WTF Source Files //
	insheet using "$SOURCE/cache/baci96_1998.dta", clear names
	foreach year of num 1999(1)2012 {
		append using "$SOURCE/baci96_`year'.dta"
	}
	//save "$SOURCE/baci96.dta", replace

	format value %12.0f

	//Log Check
	**Record Total Value by Year in Log**
	preserve
	collapse (sum) value, by(year)
	list
	restore

	if $adjust_hk == 1{
		// Values //
		merge 1:1 year icode importer ecode exporter sitc4 unit dot using "china_hk.dta", keepusing(value_adj)
		replace value = value_adj if _merge == 3 | _merge == 2 													// Replace value with adjusted values if _matched Note: Only Adjustment in Values not Quantity
		drop _merge value_adj
	}

	**Split Codes to THREE DIGIT**
	gen sitc3 = substr(sitc4,1,3)
	drop sitc4
	collapse (sum) value, by(year importer exporter sitc3)
	drop if sitc3 == "" 			//Bad Data

	drop if importer == "World"
	drop if exporter == "World"

	merge m:1 exporter using "exporter_to_eiso3c.dta", keepusing(eiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop exporter
	drop if eiso3c == "."
	merge m:1 importer using "importer_to_iiso3c.dta", keepusing(iiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop importer
	drop if iiso3c == "."

	collapse (sum) value, by(year eiso3c iiso3c sitc3)

	if $dropAX == 1{
		gen marker = regexm(sitc3, "[AX]")
		drop if marker == 1
		drop marker
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $dropNonSITCR2 == 1{
		merge m:1 sitc3 using "SITC-R2-L3-codes.dta", keepusing(marker)
		drop _merge
		keep if marker == 1
		drop marker
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $intertemporal_cntry_recode == 1{
		merge m:1 eiso3c using "eiso3c_intertemporal_recodes.dta"
		list if _merge == 2 	
		drop if _merge == 2 										//Drop unmatched from recodes file
		replace eiso3c = _recode_ if _merge == 3
		drop _merge _recode_
		merge m:1 iiso3c using "iiso3c_intertemporal_recodes.dta"
		list if _merge == 2 	
		drop if _merge == 2 										//Drop unmatched from recodes file
		replace iiso3c = _recode_ if _merge == 3
		drop _merge _recode_
		collapse (sum) value, by(year eiso3c iiso3c sitc3)
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $incomplete_cntry_recode == 1{
		merge m:1 eiso3c using "eiso3c_incomplete_recodes.dta"
		list if _merge == 2
		drop if _merge == 2  	//Drop unmatched from recodes file
		drop if _merge == 3 	//Drop Matching Countries
		drop _merge _recode_
		merge m:1 iiso3c using "iiso3c_incomplete_recodes.dta"
		list if _merge == 2
		drop if _merge == 2 	//Drop unmatched from recodes file
		drop if _merge == 3 	//Drop Matching Countries
		drop _merge _recode_
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	order year eiso3c iiso3c sitc3 value
	local fl = "nberwtf_stata_trade_sitcr2l3_1962to2000_"+"$DATASET"+".dta"
	save `fl', replace


	*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **


	****************************						
	**Dataset #2: Export Data **
	****************************

	**---------------------------------**
	**Method#1: Keep Country => "World"**
	**Note: these aggregations will capture NES as they are exports to the world **
	**---------------------------------**

	use "$SOURCE/wtf62.dta", clear
	foreach year of num 63(1)99 {
		append using "$SOURCE/wtf`year'.dta"
	}
	append using "$SOURCE/wtf00.dta"
	//save "$SOURCE/wtf.dta", replace

	format value %12.0f

	if $adjust_hk == 1{
		// Values //
		merge 1:1 year icode importer ecode exporter sitc4 unit dot using "china_hk.dta", keepusing(value_adj)
		replace value = value_adj if _merge == 3 | _merge == 2 													// Replace value with adjusted values if _matched Note: Only Adjustment in Values not Quantity
		drop _merge value_adj
	}

	**Split Codes to THREE DIGIT**
	gen sitc3 = substr(sitc4,1,3)
	drop sitc4
	collapse (sum) value, by(year importer exporter sitc3)
	drop if sitc3 == "" 			//Bad Data

	drop if exporter == "World"
	keep if importer == "World"
	drop importer

	merge m:1 exporter using "exporter_to_eiso3c.dta", keepusing(eiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop exporter
	drop if eiso3c == "." //Drops NES

	collapse (sum) value, by(year eiso3c sitc3)
	rename value value_m1

	local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
	save `fl', replace


	**------------------------------------------**
	**Method#2: Keep Country Pairs and Aggregate**
	**------------------------------------------**

	use "$SOURCE/wtf62.dta", clear
	foreach year of num 63(1)99 {
		append using "$SOURCE/wtf`year'.dta"
	}
	append using "$SOURCE/wtf00.dta"
	//save "$SOURCE/wtf.dta", replace

	format value %12.0f

	if $adjust_hk == 1{
		// Values //
		merge 1:1 year icode importer ecode exporter sitc4 unit dot using "china_hk.dta", keepusing(value_adj)
		replace value = value_adj if _merge == 3 | _merge == 2 													// Replace value with adjusted values if _matched Note: Only Adjustment in Values not Quantity
		drop _merge value_adj
	}

	**Split Codes to THREE DIGIT**
	gen sitc3 = substr(sitc4,1,3)
	drop sitc4
	collapse (sum) value, by(year importer exporter sitc3)
	drop if sitc3 == "" 			//Bad Data

	drop if exporter == "World"
	drop if importer == "World"

	merge m:1 exporter using "exporter_to_eiso3c.dta", keepusing(eiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop exporter
	drop if eiso3c == "."

	collapse (sum) value, by(year eiso3c sitc3)
	rename value value_m2

	local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
	save `fl', replace

	**
	** Compare Methods
	**
	local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
	merge 1:1 year sitc3 eiso3c using `fl'
	gen diff = value_m1 - value_m2
	codebook diff
	list if diff != 0

	**Note: Check These Methods are Equivalent**
	local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
	use `fl', clear
	//rename value_m1 value
	rename value_m2 value

	**Parse Options for Export Files**

	if $dropAX == 1{
		gen marker = regexm(sitc3, "[AX]")
		drop if marker == 1
		drop marker
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $dropNonSITCR2 == 1{
		merge m:1 sitc3 using "SITC-R2-L3-codes.dta", keepusing(marker)
		drop _merge
		keep if marker == 1
		drop marker
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $intertemporal_cntry_recode == 1{
		merge m:1 eiso3c using "eiso3c_intertemporal_recodes.dta"
		list if _merge == 2
		drop if _merge == 2 	//Drop unmatched from recodes file
		replace eiso3c = _recode_ if _merge == 3
		drop _merge _recode_
		collapse (sum) value, by(year eiso3c sitc3)
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $incomplete_cntry_recode == 1{
		merge m:1 eiso3c using "eiso3c_incomplete_recodes.dta"
		list if _merge == 2
		drop if _merge == 2 	//Drop unmatched from recodes file
		drop if _merge == 3 	//Drop Matching Countries
		drop _merge _recode_
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	order year eiso3c sitc3 value
	local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+".dta"
	save `fl', replace

	if $cleanup == 1{
		local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
		rm `fl'
		local fl = "nberwtf_stata_export_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
		rm `fl'
	}

	*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **


	************************************ 						
	**Dataset #3: Country Import Data **
	************************************ 

	**---------------------------------**
	**Method#1: Keep Country => "World"**
	**---------------------------------**

	use "$SOURCE/wtf62.dta", clear
	foreach year of num 63(1)99 {
		append using "$SOURCE/wtf`year'.dta"
	}
	append using "$SOURCE/wtf00.dta"
	//save "$SOURCE/wtf.dta", replace

	format value %12.0f

	if $adjust_hk == 1{
		// Values //
		merge 1:1 year icode importer ecode exporter sitc4 unit dot using "china_hk.dta", keepusing(value_adj)
		replace value = value_adj if _merge == 3 | _merge == 2 													// Replace value with adjusted values if _matched Note: Only Adjustment in Values not Quantity
		drop _merge value_adj
	}

	**Split Codes to THREE DIGIT**
	gen sitc3 = substr(sitc4,1,3)
	drop sitc4
	collapse (sum) value, by(year importer exporter sitc3)
	drop if sitc3 == "" 			//Bad Data

	keep if exporter == "World"
	drop if importer == "World"
	drop exporter

	merge m:1 importer using "importer_to_iiso3c.dta", keepusing(iiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop exporter
	drop if iiso3c == "." //Drops NES

	collapse (sum) value, by(year iiso3c sitc3)
	rename value value_m1

	local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
	save `fl', replace


	**------------------------------------------**
	**Method#2: Keep Country Pairs and Aggregate**
	**------------------------------------------**

	use "$SOURCE/wtf62.dta", clear
	foreach year of num 63(1)99 {
		append using "$SOURCE/wtf`year'.dta"
	}
	append using "$SOURCE/wtf00.dta"
	//save "$SOURCE/wtf.dta", replace

	format value %12.0f

	if $adjust_hk == 1{
		// Values //
		merge 1:1 year icode importer ecode exporter sitc4 unit dot using "china_hk.dta", keepusing(value_adj)
		replace value = value_adj if _merge == 3 | _merge == 2 													// Replace value with adjusted values if _matched Note: Only Adjustment in Values not Quantity
		drop _merge value_adj
	}
	
	**Split Codes to THREE DIGIT**
	gen sitc3 = substr(sitc4,1,3)
	drop sitc4
	collapse (sum) value, by(year importer exporter sitc3)
	drop if sitc3 == "" 			//Bad Data

	drop if exporter == "World"
	drop if importer == "World"

	merge m:1 importer using "importer_to_iiso3c.dta", keepusing(iiso3c)
	list if _merge == 1
	list if _merge == 2
	keep if _merge == 3 	//Keep Only Matched Items
	drop _merge
	//drop exporter
	drop if iiso3c == "."

	collapse (sum) value, by(year iiso3c sitc3)
	rename value value_m2

	local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
	save `fl', replace

	**
	** Compare Methods
	**
	local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
	merge 1:1 year sitc3 iiso3c using `fl'
	gen diff = value_m1 - value_m2
	codebook diff
	list if diff != 0

	**Note: Check These Methods are Equivalent
	local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
	use `fl', clear
	//rename value_m1 value
	rename value_m2 value

	**Parse Options**

	if $dropAX == 1{
		gen marker = regexm(sitc3, "[AX]")
		drop if marker == 1
		drop marker
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $dropNonSITCR2 == 1{
		merge m:1 sitc3 using "SITC-R2-L3-codes.dta", keepusing(marker)
		drop _merge
		keep if marker == 1
		drop marker
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $intertemporal_cntry_recode == 1{
		merge m:1 iiso3c using "iiso3c_intertemporal_recodes.dta"
		list if _merge == 2
		drop if _merge == 2		//Drop unmatched from recodes file
		replace iiso3c = _recode_ if _merge == 3
		drop _merge _recode_
		collapse (sum) value, by(year iiso3c sitc3)
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	if $incomplete_cntry_recode == 1{
		merge m:1 iiso3c using "iiso3c_incomplete_recodes.dta"
		list if _merge == 2
		drop if _merge == 2		//Drop unmatched from recodes file
		drop if _merge == 3 	//Drop Matching Countries
		drop _merge _recode_
		//Log Check
		preserve
		collapse (sum) value, by(year)
		list
		restore
	}

	order year iiso3c sitc3 value
	local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+".dta"
	save `fl', replace

	if $cleanup == 1{

	save `fl', replace
		local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method1.dta"
		rm `fl'
		local fl = "nberwtf_stata_import_sitcr2l3_1962to2000_"+"$DATASET"+"_method2.dta"
		rm `fl'
	}

log close
	
}

