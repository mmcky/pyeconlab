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

#-Level Independant SITC Options-#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

SITC_DATASET_DESCRIPTION = {
    'A' :   u"A basic dataset that collapses data to a specified level but maintaining initial countrycodes and productcodes as in the raw dataset",
    'B' :   u"Same as [A] except with intertemporally consistent country codes [1998 to Latest Available]",
    'C' :   u"Same as [B] except only includes intertemporally complete countrycodes in 1998 to 2000",
} 

#-IN WORK-#
# drop_nonsitcr2 necessary? (Is there a perfect match on the sitc concordance)
# intertemp_cntrycode necessary? (Check Meta Data)

SITC_DATASET_OPTIONS = {
    'A' :   {   
                'sitcr2' : False,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : False,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },
    'B' :   {   
                'sitcr2' : True,                      #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,              #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },
    'C' :   {   
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'intertemp_cntrycode' : False,       #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,       #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },       
}

