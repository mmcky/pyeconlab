*** ----------------------------------------------------------------***
*** Generate Basic SITC3 Country Datasets for PyEconLab 			***
*** --------------------------------------------------- 			***
*** [1] nberfeenstrawtf_do_stata_basic_country_data_bilateral.dta	***
*** [2] nberfeenstrawtf_do_stata_basic_country_data_exports.dta		***
*** [3] nberfeenstrawtf_do_stata_basic_country_data_imports.dta		***

** Datasets 
** --------
** Note: Manually Set the Following for Correspondence with Pyeconlab Datasets
** [A] global dropAX = 0, global dropNonSITCR2 = 0
** [B] global dropAX = 1, global dropNonSITCR2 = 1

*** Notes
*** -----
*** [1] Currently this requires MANUAL adjustment for directories based on REPO Locations etc
***


if c(os) == "MacOSX" {
	global dir=""
	global mac=1
}

if c(os) == "Windows" {
	global dir="E:\work-data\x_datasets\36a376e5a01385782112519bddfac85e"
	global metadir = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\dataset\NBERFeenstraWTF\meta\" 		//Hard Coded For Now
	global metaclass = "C:\Users\Matt-Work\work\repos\pyeconlab\pyeconlab\trade\classification\meta\" 				//Hard Coded For Now
	global mac=0
}

cd $dir

capture log close
log using "nberfeenstra_do_stata_sitc3_country_data.log", replace

** Settings **
global dropAX 	= 1
global dropNonSITCR2 = 1 

//Cleanup of Method1,Method2 Files
global cleanup 	= 1
 
*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **

** ------------------ ** 
** Write Concordances **
** ------------------ ** 
 
**Concord to ISO3C**
**/meta/csv/countrycodes_to_iso3c.csv contains this listing**
**Copied: 27-08-2014
**Note: This is not intertemporally consistent**

insheet using "$metadir/csv/countryname_to_iso3c.csv", clear names
gen exporter = countryname
drop countryname
rename iso3c eiso3c
save "exporter_to_eiso3c.dta", replace
insheet using "$metadir/csv/countryname_to_iso3c.csv", clear names
gen importer = countryname
drop countryname
rename iso3c iiso3c
save "importer_to_iiso3c.dta", replace

**Concord to SITC Revision 2 Level 2 Codes**
**classification/meta/SITC-R2-L3-codes.csv contains this listing**
**Copied: 28-08-2014

infix using "$metaclass/SITC-R2-L3-codes.dct", using("$metaclass/SITC-R2-L3-codes.csv") clear
save "SITC-R2-L3-codes.dta", replace

*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **
 
 
**************************************************************
**Dataset #1: Basic Bilateral Data 							**
**Removes "World" and Any Non-Country Code (i.e. NES etc.)	**
**************************************************************

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace

format value %12.0f

**Record Total Value by Year in Log**
preserve
collapse (sum) value, by(year)
list
restore

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

order year eiso3c iiso3c sitc3 value
save "nberfeenstrawtf_do_stata_basic_country_sitc3_bilateral.dta", replace


*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **


************************************ 						
**Dataset #2: Country Export Data **
************************************ 

**---------------------------------**
**Method#1: Keep Country => "World"**
**Note: these aggregations will capture NES as they are exports to the world **
**---------------------------------**

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace

format value %12.0f

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

save "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method1.dta", replace


**------------------------------------------**
**Method#2: Keep Country Pairs and Aggregate**
**------------------------------------------**

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace

format value %12.0f

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

save "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method2.dta", replace

**
** Compare Methods
**

merge 1:1 year sitc3 eiso3c using "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method1.dta"
gen diff = value_m1 - value_m2
codebook diff
list if diff != 0

**Note: These Methods are Equivalent

use "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method1.dta", clear
rename value_m1 value
order year eiso3c sitc3 value
save "nberfeenstrawtf_do_stata_basic_country_sitc3_exports.dta", replace

if $cleanup == 1{
	rm "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method1.dta"
	rm "nberfeenstrawtf_do_stata_basic_country_sitc3_exports_method2.dta"
}

*** -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- **


************************************ 						
**Dataset #3: Country Import Data **
************************************ 

**---------------------------------**
**Method#1: Keep Country => "World"**
**---------------------------------**

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace

format value %12.0f

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

save "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method1.dta", replace


**------------------------------------------**
**Method#2: Keep Country Pairs and Aggregate**
**------------------------------------------**

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace

format value %12.0f

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

save "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method2.dta", replace

**
** Compare Methods
**

merge 1:1 year sitc3 iiso3c using "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method1.dta"
gen diff = value_m1 - value_m2
codebook diff
list if diff != 0

**Note: These Methods are Equivalent

use "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method1.dta", clear
rename value_m1 value
order year iiso3c sitc3 value
save "nberfeenstrawtf_do_stata_basic_country_sitc3_imports.dta", replace

if $cleanup == 1{
	rm "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method1.dta"
	rm "nberfeenstrawtf_do_stata_basic_country_sitc3_imports_method2.dta"
}

log close
