***********************************************************************
*** Generate Test Data using STATA for PyEconLab NBERWTF Validation ***
*** --------------------------------------------------------------- ***
*** This File is to Produce General Tests Data to Support Validation **
***********************************************************************

if c(os) == "MacOSX" {
	global SOURCE_DIR="~/work-data/datasets/36a376e5a01385782112519bddfac85e/"
	global TARGET_DIR="~/work-temp/"
}

if c(os) == "Windows" {
	global SOURCE_DIR="D:/work-data/datasets/36a376e5a01385782112519bddfac85e/"
	global TARGET_DIR="D:/work-temp/"
}

*----------*
*-Settings-*
*----------*

** Uncomment this for sending output to the testing directory **
** Otherwise this will run from the current directory and can be used for updating the tests data **
//cd $TARGET_DIR

*** ---> START <---- ***

use "$SOURCE_DIR/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$SOURCE_DIR/wtf`year'.dta"
}
append using "$SOURCE_DIR/wtf00.dta"
//save "$SOURCE_DIR/wtf.dta", replace

format value %12.0f

**-----------------------**
** World Level Test Data **
**~~~~~~~~~~~~~~~~~~~~~~~**

** Time Series of World Exports 
** Filename: stata_wtf62-00_WLD_total_export
preserve
keep if exporter == "World"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "WLD"
outsheet using "stata_wtf62-00_WLD_total_export.csv", comma nolabel replace
restore

** Time Series of World Imports 
** Filename: stata_wtf62-00_WLD_total_export
preserve
keep if exporter == "World"
keep if importer == "World"
collapse (sum) value, by(year importer)
gen eiso3c = "WLD"
outsheet using "stata_wtf62-00_WLD_total_import.csv", comma nolabel replace
restore


**-----------------------**
**Country Level Test Data**
**~~~~~~~~~~~~~~~~~~~~~~~**

** Test Set#1
** Time Series of Total Exports
** Filename: stata_wtf62-00_???_total_export.csv
**
preserve
keep if exporter == "USA"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "USA"
outsheet using "stata_wtf62-00_USA_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "New Zealand"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "NZL"
outsheet using "stata_wtf62-00_NZL_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Israel"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "ISR"
outsheet using "stata_wtf62-00_ISR_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "UK"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "GBR"
outsheet using "stata_wtf62-00_GBR_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Taiwan"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "TWN"
outsheet using "stata_wtf62-00_TWN_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Switz.Liecht"
keep if importer == "World"
collapse (sum) value, by(year exporter)
gen eiso3c = "CHE"
outsheet using "stata_wtf62-00_CHE_total_export.csv", comma nolabel replace
restore


**-----------------------**
**Product Level Test Data**
**~~~~~~~~~~~~~~~~~~~~~~~**

*** SITC Level 4 ***
*** ~~~~~~~~~~~~ ***

** Product Exports over Time
** Filename: stata_wtf62-00_sitc4_####_total.csv

**Official Codes**

preserve
keep if exporter == "World"
keep if importer == "World"
keep if sitc4 == "0421"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_sitc4_0421_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "World"
keep if importer == "World"
keep if sitc4 == "8924"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_sitc4_8924_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "World"
keep if importer == "World"
keep if sitc4 == "7431"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_sitc4_7431_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "World"
keep if importer == "World"
keep if sitc4 == "6517"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_sitc4_6517_total.csv", comma nolabel replace
restore

**Unofficial Codes**

preserve
keep if exporter == "World"
keep if importer == "World"
keep if sitc4 == "6540"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_sitc4_6540_total.csv", comma nolabel replace
restore

*** SITC Level 3 ***
*** ~~~~~~~~~~~~ ***

** Product Exports over Time
** Filename: stata_wtf62-00_sitc3_####_total.csv

**Official Codes**

**Unofficial Codes**



*** SITC Level 2 ***
*** ~~~~~~~~~~~~ ***

** Product Exports over Time
** Filename: stata_wtf62-00_sitc3_####_total.csv

**Official Codes**

**Unofficial Codes**



*** SITC Level 1 ***
*** ~~~~~~~~~~~~ ***

** Product Exports over Time
** Filename: stata_wtf62-00_sitc3_####_total.csv

**Official Codes**

**Unofficial Codes**





**---------------------------------**
**Country x Product Level Test Data**
**---------------------------------**

use "$SOURCE_DIR/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$SOURCE_DIR/wtf`year'.dta"
}
append using "$SOURCE_DIR/wtf00.dta"
//save "$SOURCE_DIR/wtf.dta", replace

format value %12.0f

keep year importer exporter sitc4 value

** SITC Level 4 Data **
** ~~~~~~~~~~~~~~~~~ **

** Country x Product Exports over Time
** Filename: stata_wtf62-00_???_sitc4_####_total_export.csv
**

preserve
keep if exporter == "Denmark"
keep if importer == "World"
keep if sitc4 == "0620"
collapse (sum) value, by(year)
gen eiso3c = "DNK"
outsheet using "stata_wtf62-00_DNK_sitc4_0620_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "Spain"
keep if importer == "World"
keep if sitc4 == "8973"
collapse (sum) value, by(year)
gen eiso3c = "ESP"
outsheet using "stata_wtf62-00_ESP_sitc4_8973_total.csv", comma nolabel replace
restore


** SITC Level 3 Data **
** ~~~~~~~~~~~~~~~~~ **

use "$SOURCE_DIR/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$SOURCE_DIR/wtf`year'.dta"
}
append using "$SOURCE_DIR/wtf00.dta"
//save "$SOURCE_DIR/wtf.dta", replace

format value %12.0f

keep year importer exporter sitc4 value

**Split Codes to THREE DIGIT
gen sitc3 = substr(sitc4,1,3)
drop sitc4
collapse (sum) value, by(year importer exporter sitc3)


** Country x Product Exports over Time
** Filename: stata_wtf62-00_???_sitc3_####_total_export.csv
**

preserve
keep if exporter == "Denmark"
keep if importer == "World"
keep if sitc3 == "062"
collapse (sum) value, by(year)
gen eiso3c = "DNK"
outsheet using "stata_wtf62-00_DNK_sitc3_062_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "Spain"
keep if importer == "World"
keep if sitc3 == "897"
collapse (sum) value, by(year)
gen eiso3c = "ESP"
outsheet using "stata_wtf62-00_ESP_sitc3_897_total.csv", comma nolabel replace
restore


