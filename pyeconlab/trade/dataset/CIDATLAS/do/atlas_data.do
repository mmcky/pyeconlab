*** --------------------------------------------------------------------***
*** Generate ATLAS Stata Dataset 					***
*** --------------------------------------------------------------------***

set more off 
//set trace on
//set tracedepth 1
 
di "Loading settings for environment: " c(os)

if c(os) == "MacOSX" | c(os) == "Unix" {
	// Sources //
	global SOURCE="~/work-data/datasets/2d48c79173719bd41eb5e192fb4470b6"
	global META = "~/repos/pyeconlab/pyeconlab/trade/dataset/NBERWTF/meta" 				//Hard Coded For Now
	global METACLASS = "~/repos/pyeconlab/pyeconlab/trade/classification/meta" 			//Hard Coded For Now
	// Targets //
	global WORKINGDIR="~/work-temp"
}

/*
if c(os) == "Windows" {
	global SOURCE="D:\work-data\datasets\2d48c79173719bd41eb5e192fb4470b6"
	global META = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\dataset\NBERWTF\meta" 		//Hard Coded For Now
	global METACLASS = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\classification\meta" 	//Hard Coded For Now
	// Targets //
	global WORKINGDIR="D:/work-temp"
}
*/

cd $WORKINGDIR

***----------------***
***---Trade DATA---***
***----------------***

insheet using "$SOURCE/year_origin_destination_sitc.tsv", tab clear

//Fix SITC4 Codes//
tostring(sitc4), replace
gen length = strlen(sitc4)
codebook length
replace sitc4="0"+sitc4 if length == 3
replace sitc4="00"+sitc4 if length == 2
replace sitc4="000"+sitc4 if length == 1
drop length

//Year Coverage//
codebook year

//Country Codes//
rename origin eiso3c
replace eiso3c = upper(eiso3c)
rename destination iiso3c
replace iiso3c = upper(iiso3c)

//Values//
gen CHECK = 1 if export_val == 0 & import_val == 0
codebook CHECK 				 			//Should be no overlap all missing values
drop CHECK
gen CHECK = 1 if export_val == . & import_val == . 		//Should be no overlap all missing values
codebook CHECK
di "These need to be investigated as . values"
drop CHECK

/// Current Issues with RESHAPE and Uniqueness ///
duplicates tag year eiso3c iiso3c sitc4, generate(dup)

count
rename export_val val_export
rename import_val val_import
reshape long val_, i(year eiso3c iiso3c sitc4) j(dot) string
count

/// WORKING HERE ////


//Trade Data for Levels 3,2,1 //
foreach level in 3 2 1 {
	di "Producing trade datasets for Level: `level'"
	// Export //
	use "cidatlas_sitcr2l4_trade_1962to2012.dta", clear
	gen sitc`level' = substr(sitc4,1,`level')
	collapse (sum) value, by(year eiso3c sitc`level')
	save "cidatlas_sitcr2l`level'_trade_1962to2012.dta", replace
}



***----------------------------***
***---Export and Import DATA---***
***----------------------------***

**-- SITC -- **

insheet using "$SOURCE/year_origin_sitc.tsv", tab clear

//Fix SITC4 Codes//
tostring(sitc4), replace
gen length = strlen(sitc4)
codebook length
replace sitc4="0"+sitc4 if length == 3
replace sitc4="00"+sitc4 if length == 2
replace sitc4="000"+sitc4 if length == 1
drop length

//Year Coverage//
codebook year

//Exports Dataset//
preserve
rename origin eiso3c 		
replace eiso3c = upper(eiso3c)
rename export_val value
keep year eiso3c sitc4 value
save "cidatlas_sitcr2l4_export_1962to2012.dta", replace
restore

//Export RCA Dataset//
preserve
rename origin eiso3c 		
replace eiso3c = upper(eiso3c)
rename export_rca rca
keep year eiso3c sitc4 rca
save "cidatlas_sitcr2l4_export_rca_1962to2012.dta", replace
restore

//Import Dataset//
preserve
rename origin iiso3c
replace iiso3c = upper(iiso3c)
rename import_val value
keep year iiso3c sitc4 value
save "cidatlas_stata_sitcr2l4_import_1962to2012.dta", replace
restore

//Import RCA Dataset//
preserve
rename origin iiso3c
replace iiso3c = upper(iiso3c)
rename import_rca rca
keep year iiso3c sitc4 rca
save "cidatlas_stata_sitcr2l4_import_rca_1962to2012.dta", replace
restore

//Export and Import Data for Levels 3,2,1 //
foreach level in 3 2 1 {
	di "Producing export and import datasets for Level: `level'"
	// Export //
	use "cidatlas_sitcr2l4_export_1962to2012.dta", clear
	gen sitc`level' = substr(sitc4,1,`level')
	collapse (sum) value, by(year eiso3c sitc`level')
	save "cidatlas_sitcr2l`level'_export_1962to2012.dta", replace
	// Import //
	use "cidatlas_stata_sitcr2l4_import_1962to2012.dta", clear
	gen sitc`level' = substr(sitc4,1,`level')
	collapse (sum) value, by(year iiso3c sitc`level')
	save "cidatlas_sitcr2l`level'_import_1962to2012.dta", replace
}


**--HS--**
