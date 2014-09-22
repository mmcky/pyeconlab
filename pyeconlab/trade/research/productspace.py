"""
Special or Experimental Research Functions for Trade
"""


def productspace_5yearavg_improbableemergence(Mcp_ImProbableProducts, GDPGrowth, verbose=False):
	""" Construct a table:
 					-5Y, -4Y ... 0Y ... 4Y, 5Y
	<country>  		 GDPGrowth
	"""

a = from_dict_to_dataframe(Mcp_ImProbableProducts)
b = WDIData["GDPGrowth"]

r = {}
for idx,s in  a.iterrows():
    year, country, productcode = idx
    value = s['ImProbProducts']
    if value > 0:
        r[(year, country)] = 1 

df = pd.DataFrame.from_dict(r, orient='index')
df.index = pd.Index(r.keys()) 	#They are all 1's (this will need to change if they aren't all 1's)
df.columns = ['ImProb']
df.index.names = ['year', 'country']
df.sort_index(inplace=True)


r = {}
for idx, s in df.iterrows():
	year, country = idx 
	for yr in range(year-5, year+5, 1):
		if yr < 1963:
			continue
		if yr > 2012:
			continue
		try:
			gdpgrowth = b.ix[(country, yr)]
		except:
			gdpgrowth = np.nan
		r[(yr, country)] = gdpgrowth 

df = pd.DataFrame.from_dict(r, orient='index')
# df.index = pd.Index(r.keys()) 	#They are all 1's (this will need to change if they aren't all 1's)
df.columns = ['ImProb']
# df.index.names = ['year', 'country']
# df.sort_index(inplace=True)








#-Wide Approach-#
df = df.unstack(level=['year'])