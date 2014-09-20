"""
Pandas Dynamic Converters
"""

def reindex_dynamic_dataframe(df, year_pairs='years', verbose=False):
    ''' Converts a dynamicaly referenced Dataframe (i.e. '1962-1963') to a dataframe with index to_year and from_year
    '''
    new_index = []
    for item in df.index:
        (years, country, productcode) = item
        from_year = years.split('-')[0]
        to_year = years.split('-')[1]
        new_index.append((int(from_year), int(to_year), country, productcode))
    new_index = pd.MultiIndex.from_tuples(new_index, names=['from_year', 'to_year', 'country', 'productcode'])
    new_df = df.copy()
    new_df.index = new_index
    return new_df

def reindex_dynamic_dict(data_dict, base='start', verbose=False):
    ''' Converts a Dynamic Dict (Year-Year) to be indexed by either start or finish year
        Options:    base    start -> Reindexes Dictionary by Start Year
                            finish -> Reindexes Dictionary by Finish Year
    ''' 
    new_dict = dict()
    for key in data_dict.keys():
        start_year = int(key.split('-')[0])
        finish_year = int(key.split('-')[1])
        if verbose: print "Key: %s, Start_Year: %s, Finish_Year: %s" % (key, start_year, finish_year)
        if str(base).lower() == 'start':
            new_dict[start_year] = data_dict[key]
        elif str(base).lower() == 'finish':
            new_dict[finish_year] = data_dict[key]
        else:
            print "Error: base needs to be 'start' year or 'finish' year"
    return new_dict