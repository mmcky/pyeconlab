"""
NBER (Self Contained) Dataset Functions

Source Dataset: SITC R2 (Quasi) Level 4

Status: IN-TESTING

This is a generalised version of:
	1. constructor_dataset_sitcr2l3
	2. constructor_dataset_sitcr2l4

Future Work
-----------
1. Write Tests comparing this with constructor_dataset_sitcr2l3 and constructor_dataset_sitcr2l4 (to see if I can remove others)
2. Write Independant Tests

"""

#-Generalised SC Constructor Functions-#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def construct_sitcr2(df, data_type, level, dropAX=True, sitcr2=True, drop_nonsitcr2=True, adjust_hk=(False, None), intertemp_cntrycode=False, drop_incp_cntrycode=False, adjust_units=False, source_institution='un', verbose=True):
        """
        Construct a Self Contained (SC) Direct Action Dataset for Countries at the SITC Revision 2 Level 3
        
        There are no checks on the incoming dataframe to ensure data integrity.
        This is your responsibility

        STATUS: tests/test_constructor_dataset_sitcr2l3.py

        Parameters
        ----------
        df                  :   DataFrame
                                Pandas DataFrame containing the raw data
        data_type           :   str
                                Specify what type of data 'trade', 'export', 'import'
        level               :   int
                                Specify Level of Final dataset (i.e. SITC Level 1, 2, 3, or 4)
        dropAX              :   bool, optional(default=True)
                                Drop AX Codes 
        sitcr2              :   bool, optional(default=True)
                                Add SITCR2 Indicator
        drop_nonsitcr2      :   bool, optional(default=True)
                                Drop non-standard SITC2 Codes
        adjust_hk           :   Tuple(bool, df), optional(default=(False, None))
                                Adjust the Hong Kong Data using NBER supplemental files which needs to be supplied as a dataframe
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

            [1] Adjust Hong Kong and China Data
            [2] Drop SITC4 to SITC3 Level (for greater intertemporal consistency)
            [3] Import ISO3C Codes as Country Codes
            [4] Drop Errors in SITC3 codes ["" Codes]
            
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
        idx = ['year', 'exporter', 'importer', 'sitc4']
        df = df[idx + ['value']]
        
        #-Operations Requiring SITC Level 4-#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #-Hong Kong China Data Adjustment Option-#
        if adjust_hk[0]:
            if verbose: print "[INFO] Adjusting Hong Kong and China Values"
            hkdata = adjust_hk[1]
            #-Values-#
            raw_value = df[idx+['value']].rename(columns={'value' : 'value_raw'})
            try:
                adjust_value = hkdata[idx+['value_adj']]
            except:
                raise ValueError("[ERROR] China/Hong Kong Data has not been passed in properly!")
            #-Note: Current merge_columns utility merges one column set at a time-#
            df = merge_columns(raw_value, adjust_value, idx, collapse_columns=('value_raw', 'value_adj', 'value'), dominant='right', output='final', verbose=verbose)
            #-Note: Adjust Quantity has not been implemented. See NBERWTF constructor -#

        #-Collapse to SITC Level -#
        if level != 4:
            if verbose: print "[INFO] Collapsing to SITC Level %s Data" % level
            df['sitc%s'%level] = df.sitc4.apply(lambda x: x[0:level])
            df = df.groupby(['year', 'exporter', 'importer', 'sitc3']).sum()['value'].reset_index()
        elif level == 4:
            if verbose: print "[INFO] Data is already at the requested level"
        else:
            raise ValueError("Level must be 1, 2, 3, or 4 for the NBER data")

        #-Operations Post Collapse to SITC Level-#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #-Countries Only Adjustment-#
        if verbose: print "[INFO] Removing 'World' values from the dataset to be country only data"
        df = df.loc[(df.exporter != "World") & (df.importer != "World")]
        
        #-Add Country ISO Information-#
        #-Exports (can include NES on importer side)-#
        if data_type == 'export' or data_type == 'exports':
            if verbose: print "[INFO] Adding eiso3c using nber meta data"
            df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.eiso3c != '.')]
            df = df.groupby(['year', 'eiso3c', 'sitc3']).sum()['value'].reset_index()
        #-Imports (can include NES on importer side)-#
        elif data_type == 'import' or data_type == 'imports':
            if verbose: print "[INFO] Adding iiso3c using nber meta data"
            df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.iiso3c != '.')]
            df = df.groupby(['year','iiso3c', 'sitc3']).sum()['value'].reset_index()
        #-Trade-#
        else: 
            if verbose: print "[INFO] Adding eiso3c and iiso3c using nber meta data"
            df['iiso3c'] = df.importer.apply(lambda x: countryname_to_iso3c[x])
            df['eiso3c'] = df.exporter.apply(lambda x: countryname_to_iso3c[x])
            df = df.loc[(df.iiso3c != '.') & (df.eiso3c != '.')]
            df = df.groupby(['year', 'eiso3c', 'iiso3c', 'sitc3']).sum()['value'].reset_index()
        
        #-Remove Product Code Errors in Dataset-#
        df = df.loc[(df['sitc%s'%level != "")]                                                                   #Does this need a reset_index?
        #-dropAX-#
        if dropAX:
            if verbose: print "[INFO] Dropping SITC Codes with 'A' or 'X'"
            df['AX'] = df['sitc%s'%level].apply(lambda x: 1 if re.search("[AX]", x) else 0)
            df = df.loc[df.AX != 1]
            del df['AX']
        
        #-Official SITCR2 Codes-#
        if sitcr2:
            if verbose: print "[INFO] Adding SITCR2 Indicator"
            sitc = SITC(revision=2, source_institution=source_institution)
            codes = sitc.get_codes(level=lelve)
            df['sitcr2'] = df['sitc%s'%level].apply(lambda x: 1 if x in codes else 0)
            if drop_nonsitcr2:
                if verbose: print "[INFO] Dropping Non Standard SITCR2 Codes"
                df = df.loc[(df.sitcr2 == 1)]
                del df['sitcr2']                #No Longer Needed
        
        #-Adjust Country Codes to be Intertemporally Consistent-#
        if intertemp_cntrycode:
            #-Export-#
            if data_type == 'export' or data_type == 'exports':
                if verbose: print "[INFO] Imposing dynamically consistent eiso3c recodes across 1962-2000"
                df['eiso3c'] = df['eiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df = df[df['eiso3c'] != '.']
                df = df.groupby(['year', 'eiso3c', 'sitc3']).sum().reset_index()
            #-Import-#
            elif data_type == 'import' or data_type == 'imports':
                if verbose: print "[INFO] Imposing dynamically consistent iiso3c recodes across 1962-2000"
                df['iiso3c'] = df['iiso3c'].apply(lambda x: concord_data(iso3c_recodes_for_1962_2000, x, issue_error=False))    #issue_error = false returns x if no match
                df = df[df['iiso3c'] != '.']
                df = df.groupby(['year', 'iiso3c', 'sitc3']).sum().reset_index()
            #-Trade-#
            else:
                if verbose: print "[INFO] Imposing dynamically consistent iiso3c and eiso3c recodes across 1962-2000"
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
            if verbose: print "[INFO] Adjusting 'value' units to $'s"
            df['value'] = df['value']*1000         #Default: Keep in 1000's
        
        #-Return Dataset-#
        if verbose: print "[INFO] Finished Computing Dataset (%s) ..." % (data_type) 
        return df