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

"""

#-SITC Level 1 Dataset-#

#-SITC Level 2 Dataset-#

#-SITC Level 3 Dataset-#

datasets_sitc3  = {
    'Method'                :   'SC_CNTRY_SR2L3_Y62to00',
    #-Trade-#

    #-Export-#
    'Export-SITCR2L3-A'         :   {
                                        'Description'   :   'A Simple Dataset that contains AX, non SITC Standard Codes and and country codes are not intetemporally consistent',  \
                                        'Settings'      :   'dropAX=False, sitcr2=False, drop_nonsitcr2=False, intertemp_cntrycode=False, drop_incp_cntrycode=False',   \
                                        'SpecialMethod' :   'construct_dataset_SC_CNTRY_SR2L3_Y62to00_A'                                                                \
                                    },  
    'Export-SITCR2L3-B'         :   {
                                        'Description'   :   'A Dataset that does not contain AX, or non standard codes, and country codes are not intetemporally consistent', \
                                        'Settings'      :   'dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False',      \
                                        'SpecialMethod' :   'construct_dataset_SC_CNTRY_SR2L3_Y62to00_B'                                                                \
                                    },
    'Export-SITCR2L3-C'         :   {
                                        'Description'   :   'A Dataset that does not contain AX or non standard codes, and has intertemporally consistent country codes',   \
                                        'Settings'      :   'dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=False',           \
                                        'SpecialMethod' :   'construct_dataset_SC_CNTRY_SR2L3_Y62to00_C'                                                                    \
                                    },         
    'Export-SITCR2L3-D'         :   {
                                        'Description'   :   'A Dataset that does not contain AX or non standard codes, and has intertemporally consistent country codes and countries covering the entire period',   \
                                        'Settings'      :   'dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=True, drop_incp_cntrycode=True',           \
                                        'SpecialMethod' :   'construct_dataset_SC_CNTRY_SR2L3_Y62to00_D'                                                                   \
                                    }, 
    #-Import-#
}

#-SITC Level 4 Dataset-#
datasets_sitc4 = {    

}