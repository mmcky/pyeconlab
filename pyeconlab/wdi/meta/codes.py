"""
Meta Subpackage for WDI
"""


class WDISeriesCodes():
	"""
	Container for Easy to Remember WDI Series Codes (World Bank)
	"""
	GDP = r'NY.GDP.MKTP.CD'
	GDPPC = r'NY.GDP.PCAP.CD'
	GDPGrowth = r'NY.GDP.MKTP.KD.ZG'
	GDPPCGrowth = r'NY.GDP.PCAP.KD.ZG'

CodeToName = {
	r'NY.GDP.MKTP.CD' 		: 'GDP',
	r'NY.GDP.PCAP.CD' 		: 'GDPPC',
	r'NY.GDP.MKTP.KD.ZG' 	: 'GDPGrowth',
	r'NY.GDP.PCAP.KD.ZG' 	: 'GDPPCGrowth',
}