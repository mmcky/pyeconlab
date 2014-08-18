*** Generate Test Data for PyEconLab ***
*** stata_filename.csv 				 ***

if c(os) == "MacOSX" {
	global dir=""
	global mac=1
}

if c(os) == "Windows" {
	global dir="E:\work-data\x_datasets\36a376e5a01385782112519bddfac85e"
	global mac=0
}

cd $dir

use "$dir/wtf62.dta", clear
foreach year of num 63(1)99 {
	append using "$dir/wtf`year'.dta"
}
append using "$dir/wtf00.dta"
//save "$dir/wtf.dta", replace


**-----------------------**
**Country Level Test Data**
**-----------------------**

format value %12.0f

** Test Set#1
** Time Series of Total Exports
** Filename: stata_wtf62-00_???_total_export.csv
**
preserve
keep if exporter == "USA"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_USA_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "New Zealand"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_NZL_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Israel"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_ISR_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "UK"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_GBR_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Taiwan"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_TWN_total_export.csv", comma nolabel replace
restore

preserve
keep if exporter == "Switz.Liecht"
keep if importer == "World"
collapse (sum) value, by(year exporter)
outsheet using "stata_wtf62-00_CHE_total_export.csv", comma nolabel replace
restore



**-----------------------**
**Product Level Test Data**
**-----------------------**

** Test Set#2
** Product Exports over Time
** Filename: stata_wtf62-00_sitc4_####_total.csv
**

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



**-------------------------------**
**Country Product Level Test Data**
**-------------------------------**

** Test Set#3
** Country x Product Exports over Time
** Filename: stata_wtf62-00_???_sitc4_####_total_export.csv
**

preserve
keep if exporter == "Denmark"
keep if importer == "World"
keep if sitc4 == "0620"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_DNK_sitc4_0620_total.csv", comma nolabel replace
restore

preserve
keep if exporter == "Spain"
keep if importer == "World"
keep if sitc4 == "8973"
collapse (sum) value, by(year)
outsheet using "stata_wtf62-00_ESP_sitc4_8973_total.csv", comma nolabel replace
restore

**-----------------------**
**Special Group Test Data**
**-----------------------**


