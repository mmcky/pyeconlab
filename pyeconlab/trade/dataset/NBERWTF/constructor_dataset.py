"""
NBER (Self Contained) Dataset Functions
=======================================

This family of files holds functions that Generate Specific Datasets that are Self Contained.
The benefit of being self contained is that they are easier to debug then using the Constructor Class. 
Therefore, it is best to explore using the Constructor and then develop a dataset

Notes
-----
1. This reduces the size of the Constructor Class and Allows direct access to methods that compile datasets if desired. 
2. Independantly verifiable functions for testing (without the complexity of the Constructor class)

Note: These are avaiable as Trade, Export or Import. 

"""

#-SITC Level 1 Dataset-#

#-SITC Level 2 Dataset-#

#-SITC Level 3 Dataset-#

SITC3_DATA_DESCRIPTION = {
    'A' :   u"A basic dataset that collapses data to SITC Level 3 but maintaining initial countrycodes and productcodes as in the raw dataset"
    'B' :   u"[A] except corrects HK-CHINA data from nber correction files"
    'C' :   u"A dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, but does not adjust countries for intertemporal consistency"
    'D' :   u"A Dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, and has intertemporally consistent country codes",
    'E' :   u"A Dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, has intertemporally consistent country codes, and includes countries that only cover the entire period",
} 

SITC3_DATASET_OPTIONS = {
    'A' :   {   'dropAX' : False,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : False,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : False,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : False,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
                'verbose' : True,
            },
    'B' :   {   'dropAX' : False,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : False,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : False,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                   #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
                'verbose' : True,
            },
    'C' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,       #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,       #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
                'verbose' : True,
            },       
    'D' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : True,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,       #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
                'verbose' : True,
            },           
    'E' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : True,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : True,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
                'verbose' : True,
            },
}


#-SITC Level 4 Dataset-#
datasets_sitc4 = {    

}