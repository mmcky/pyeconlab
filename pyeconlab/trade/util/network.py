import pandas as pd

def compute_average_centrality(mcp, proximity, normalized=True, sum_not_mean=False):
    ''' Compute Average Centrality from Mcp and Proximity matrices
        Status: IN-TESTING
        Note: normalized = [TRUE] Divide by Total Number of Products; [FALSE] Divide by number of products exported by that country
        Note: sum_not_mean = sum's the mean proximity multiplied by countries export basket [Hausman uses SUM() rather than normalised mean -> Same Overall Graph Shape!]
        Return: Dict()
    '''
    if type(mcp) == dict and type(proximity == dict):
        avg_centrality = dict()
        years = mcp.keys()                          #should this be the SET of KEYS for both mcp and proximity?    
        for year in years:
            if normalized:
                avg_centrality[year] = mcp[year].mul(proximity[year].mean(), axis=1).mean(axis=1)
                if sum_not_mean: avg_centrality[year] = mcp[year].mul(proximity[year].mean(), axis=1).sum(axis=1)       #05/07/2013 -> change from mcp. to mcp[year].
            else:
                centrality = proximity[year].sum() / len(proximity[year])                                               # Explicit FORM; num_products = len(proximity[year])
                country_centrality = centrality * mcp[year]
                num_prods_exported = mcp[year].sum(axis=1) 
                avg_centrality[year] = (country_centrality.sum(axis=1) / num_prods_exported)
        return avg_centrality
    else:
        if normalized: 
            avg_centrality = mcp.mul(proximity.mean(), axis=1).mean(axis=1)
            if sum_not_mean: avg_centrality = mcp.mul(proximity.mean(), axis=1).sum(axis=1)                                    
        else:
            num_prods_exported = mcp.sum(axis=1)                                                                        # Condensed FORM
            avg_centrality =  mcp.mul(proximity.mean(), axis=1).sum(axis=1).div(num_prods_exported)
    return avg_centrality

