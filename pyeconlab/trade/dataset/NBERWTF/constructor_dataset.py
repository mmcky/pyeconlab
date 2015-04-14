"""
NBER (Self Contained) Dataset Functions
=======================================

Type: {{ Configuration File }}

This family of files holds functions that Generate Specific Datasets that are Self Contained. 
The benefit of being self contained is that they are easier to debug then using the Constructor Class 
rather than test all permutations of the Constructor methods. 

Therefore, it is best to explore using the Constructor and then develop an SC dataset constructor.

Note: The below configurations are avaialable as Trade, Export or Import. 

Notes
-----
1. This reduces the size of the Constructor Class and allows for direct external access to methods that compile datasets if desired. 
2. Independantly verifiable functions for testing (without the complexity of the Constructor class)

Future Work
-----------
1. Should the Dataset Descriptions be moved to the relevant constructor file and remove this file?
2. Should I write hierarchical code (i.e. use SITC4 to conduct majority of work and then collapse?) 
This complicates some issues such as dropAX as this should be done AFTER the collapse to maximise Level 3 information
[For Now] Write Independant Functions (despite code duplication)
3. Update this for full set of Datasets

"""

#------------------------------#
#-Dataset Configuration Values-#
#------------------------------#

#-Level Independant SITC Options-#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

SITC_DATASET_DESCRIPTION = {
    'A' :   u"A basic dataset that collapses data to a specified level but maintaining initial countrycodes and productcodes as in the raw dataset",
    'B' :   u"[A] except corrects HK-CHINA data from nber correction files",
    'C' :   u"A dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, but does not adjust countries for intertemporal consistency",
    'D' :   u"A Dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, and has intertemporally consistent country codes",
    'E' :   u"A Dataset that does not contain AX or any non standard codes, adjusts HK-CHINA data, has intertemporally consistent country codes, and includes countries that only cover the entire period",
} 

# [A] dropAX=False, sitcr2=False, drop_nonsitcr2=False, adjust_hk=False, intertemp_cntrycode=False, drop_incp_cntrycode=False
# [B] dropAX=False, sitcr2=False, drop_nonsitcr2=False, adjust_hk=True, intertemp_cntrycode=False, drop_incp_cntrycode=False
# [C] dropAX=True, sitcr2=True, drop_nonsitcr2=True, adjust_hk=True, intertemp_cntrycode=False, drop_incp_cntrycode=False
# [D] dropAX=True, sitcr2=True, drop_nonsitcr2=True, adjust_hk=True, intertemp_cntrycode=True, drop_incp_cntrycode=False 
# [E] dropAX=True, sitcr2=True, drop_nonsitcr2=True, adjust_hk=True, intertemp_cntrycode=True, drop_incp_cntrycode=True 

SITC_DATASET_OPTIONS = {
    'A' :   {   'dropAX' : False,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : False,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : False,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : False,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },
    'B' :   {   'dropAX' : False,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : False,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : False,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                   #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },
    'C' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : False,       #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,       #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },       
    'D' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : True,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : False,       #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },           
    'E' :   {   'dropAX' : True,                     #Drops Products where Codes have 'A' or 'X'
                'sitcr2' : True,                     #Adds an Official SITC Revision 2 Indicator
                'drop_nonsitcr2' : True,             #Removes Non-Official SITC Revision 2 Codes From the Dataset
                'adjust_hk' : True,                  #Adjust Data to incorporate Honk Kong Adjusments provided by NBER
                'intertemp_cntrycode' : True,        #Recode Country Codes to be Intertemporally Consistent
                'drop_incp_cntrycode' : True,        #Drop Incomplete Intertemporal Countries
                'adjust_units' : False,
                'source_institution' : 'un',
            },
}




