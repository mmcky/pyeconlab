"""
NBER (Self Contained) Dataset Functions [SITC Revision 2 Level 3]

Source Dataset: SITC R2 (Quasi) Level 4

Notes
-----
1. Self Contained Compilation Reduces the Need to Debug many other routines. Use the Constructor class to explore the raw data 

"""

import re

from pyeconlab.trade.classification import SITC
from pyeconlab.util import concord_data
from .meta import countryname_to_iso3c, iso3c_recodes_for_1962_2000, incomplete_iso3c_for_1962_2000 
            

#-Constructors-#

def construct_sitcr2l3(df, data_type, dropAX=True, sitcr2=True, drop_nonsitcr2=True, intertemp_cntrycode=False, drop_incp_cntrycode=False, adjust_units=False, source_institution='un', verbose=True):
        """
        Construct a Self Contained (SC) Direct Action Dataset for Countries at the SITC Revision 2 Level 3
        
        There are no checks on the dataframe to ensure data integrity.
        This is your responsibility

        STATUS: tests/test_constructor_dataset_sitcr2l3.py

        Parameters
        ----------
        df                  :   DataFrame
                                Pandas DataFrame containing the raw data
        data_type           :   str
                                Specify what type of data 'trade', 'export', 'import'
        dropAX              :   bool, optional(default=True)
                                Drop AX Codes 
        sitcr2              :   bool, optional(default=True)
                                Add SITCR2 Indicator
        drop_nonsitcr2      :   bool, optional(default=True)
                                Drop non-standard SITC2 Codes
        intertemp_cntrycode :   bool, optional(default=False)
                                Generate Intertemporal Consistent Country Units (from meta)
        drop_incp_cntrycode :   bool, optional(default=False)
                                Drop Incomplete Country Codes (from meta)
        adjust_units        :   bool, optional(default=False)
                                Adjust units by a factor of 1000 to specify in $'s
        source_institution  :   str, optional(default='un')
                                which institutions SITC classification to use

        Notes
        -----
        1. Operations ::

            [1] Drop SITC4 to SITC3 Level (for greater intertemporal consistency)
            [2] Import ISO3C Codes as Country Codes
            [3] Drop Errors in SITC3 codes ["" Codes]
            
            Optional:
            ---------
            [A] Drop sitc3 codes that contain 'A' and 'X' codes [Default: True]
            [B] Drop Non-Standard SITC3 Codes [i.e. Aren't in the Classification]
            [C] Adjust iiso3c, eiso3c country codes to be intertemporally consistent
            [D] Drop countries with incomplete data across 1962 to 2000 (strict measure)
  

        3. This makes use of countryname_to_iso3c in the meta data subpackage
        4. This method can be tested using /do/basic_sitc3_country_data.do
        5. DropAX + Drop NonStandard SITC Rev 2 Codes still contains ~94-96% of the data found in the raw data

        ..  Future Work
            -----------
            1. Check SITC Revision 2 Official Codes
            2. Add in a Year Filter
        """

        #-Set Data-#
        df = df[['year', 'exporter', 'importer', 'sitc4', 'value']]
        
        #-Adjust to SITC Level 3-#
        df['sitc3'] = df.sitc4.apply(lambda x: x[0:3])
        df = df.groupby(['year', 'exporter', 'importer', 'sitc3']).sum()['value'].reset_index()
        
        #-Countries Only Adjustment-#
        df = df.loc[(df.exporter != "World") & (df.importer != "World")]
        
        #-Add Country ISO Information-#
        #-Exports (can include NES on importer side)-#
        if data_type == 'export' or data_type == 'exports':
            df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.eiso3c != '.')]
            df = df.groupby(['year', 'eiso3c', 'sitc3']).sum()['value'].reset_index()
        #-Imports (can include NES on importer side)-#
        elif data_type == 'import' or data_type == 'imports':
            df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.iiso3c != '.')]
            df = df.groupby(['year','iiso3c', 'sitc3']).sum()['value'].reset_index()
        #-Trade-#
        else: 
            df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
            df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.iiso3c != '.') & (df.eiso3c != '.')]
            df = df.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum()['value'].reset_index()
        
        #-Remove Product Code Errors in Dataset-#
        df = df.loc[(df.sitc3 != "")]                                                                   #Does this need a reset_index?
        #-dropAX-#
        if dropAX:
            if verbose: print "[INFO] Dropping SITC Codes with 'A' or 'X'"
            df['AX'] = df.sitc3.apply(lambda x: 1 if re.search("[AX]", x) else 0)
            df = df.loc[df.AX != 1]
            del df['AX']
        
        #-Official SITCR2 Codes-#
        if sitcr2:
            if verbose: print "[INFO] Adding SITCR2 Indicator"
            sitc = SITC(revision=2, source_institution=source_institution)
            codes = sitc.get_codes(level=3)
            df['sitcr2'] = df['sitc3'].apply(lambda x: 1 if x in codes else 0)
            if drop_nonsitcr2:
                if verbose: print "[INFO] Dropping Non Standard SITCR2 Codes"
                df = df.loc[(df.sitcr2 == 1)]
                del df['sitcr2']                #No Longer Needed
        
        #-Adjust Country Codes to be Intertemporally Consistent-#
        if intertemp_cntrycode:
            if verbose: print "[INFO] Imposing dynamically consistent iiso3c and eiso3c recodes across 1962-2000"
            #-Export-#
            if data_type == 'export' or data_type == 'exports':
                df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df = df[df['eiso3c'] != '.']
                df = df.groupby(['year', 'eiso3c', 'sitc3']).sum().reset_index()
            #-Import-#
            elif data_type == 'import' or data_type == 'imports':
                df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df = df[df['iiso3c'] != '.']
                df = df.groupby(['year', 'iiso3c', 'sitc3']).sum().reset_index()
            #-Trade-#
            else:
                df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df = df[df['iiso3c'] != '.']
                df = df[df['eiso3c'] != '.']
                df = df.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum().reset_index()
        
        #-Drop Incomplete Country Codes-#
        if drop_incp_cntrycode:
            if verbose: print "[INFO] Dropping countries with incomplete data across 1962-2000"
            #-Export-#
            if data_type == 'export' or data_type == 'exports':
                df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False))     #issue_error = false returns x if no match
                df = df[df['eiso3c'] != '.']
            #-Import-#
            elif data_type == 'import' or data_type == 'imports':
                df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False))     #issue_error = false returns x if no match
                df = df[df['iiso3c'] != '.']
            #-Trade-#
            else:
                df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False))     #issue_error = false returns x if no match
                df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(incomplete_iso3c_for_1962_2000, x, issue_error=False))     #issue_error = false returns x if no match
                df = df[df['iiso3c'] != '.']
                df = df[df['eiso3c'] != '.']
            df = df.reset_index()
            del df['index']
       
        #-Adjust Units from 1000's to $'s-#
        if adjust_units:
            df['value'] = df['value']*1000         #Default: Keep in 1000's
        
        #-Return Dataset-#
        return df
