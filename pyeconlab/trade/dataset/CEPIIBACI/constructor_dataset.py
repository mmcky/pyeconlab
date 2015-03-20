"""
BACI (Self Contained) Predefined Dataset Definitions
====================================================

STATUS: IN-WORK

{{ Configuration / Definitions File }}

This family of files holds functions that Generate Specific Datasets from the source data. 
The benefit of being self contained is that they are easier to debug then using the Constructor Class Methods
rather than test all permutations of the Constructor methods. 

Therefore, it is best to explore using the Constructor and then develop an SC dataset constructor.

Note: The below configurations are available as Trade, Export or Import. 

"""

#------------------------------#
#-Dataset Configuration Values-#
#------------------------------#

SITC_DATASET_DESCRIPTION = {
    'A' :   u"A basic dataset that collapses data to a specified level but maintaining initial countrycodes and productcodes as in the raw dataset",
    'B' :   u"Same as [A] except with intertemporally consistent country codes [1998 to Latest Available]",
    'C' :   u"Same as [B] except only includes intertemporally complete countrycodes in 1998 to 2000",
} 

#-IN WORK-#
# intertemp_cntrycode necessary? (Check Meta Data)

SITC_DATASET_OPTIONS = {
    'A' :   {   
                'check_concordance' : True,           #Check Entire Concordance has matched internal product codes
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,               #Adjust Units from 1000's of $'s to $'s
                'concordance_institution' : 'un',     #Specify concordance source institution
            },
    'B' :   {   
                'check_concordance' : True,           #Check Entire Concordance has matched internal product codes
                'intertemp_cntrycode' : True,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,               #Adjust Units from 1000's of $'s to $'s
                'concordance_institution' : 'un',     #Specify concordance source institution
            },
    'C' :   {   
                'check_concordance' : True,           #Check Entire Concordance has matched internal product codes
                'intertemp_cntrycode' : True,         #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : True,         #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,               #Adjust Units from 1000's of $'s to $'s
                'concordance_institution' : 'un',     #Specify concordance source institution
            },       
}

