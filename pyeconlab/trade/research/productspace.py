"""
Special or Experimental Research Functions for Trade
"""


def productspace_5yearavg_improbableemergence(Mcp_ImProbableProducts, GDPGrowth, verbose=False):
	""" Construct a table:
 					-5Y, -4Y ... 0Y ... 4Y, 5Y
	<country>  		 GDPGrowth
	"""

	for idx,s in  a.iterrows():
    year, country, productcode = idx
    value = s['ImProbProducts']
    if value > 0:
        rval.append(value)
        ridx.append(idx)