"""
A Basic Ricardian Trade Model 2 x 2 x 1
"""

from __future__ import division

class Country(object):
	"""
	An object that represents a Country

	Parameters
	----------
	name 			: 	str
						Provide a country name
	endowment 		: 	int
						Provide an Endowment of Labour (Hours)
	products 		: 	tuple(str, str)
						Provide Product Names
	productivity 	: 	tuple(float, float)
						Provide Productivity Values where positions equals product position
	quantaties 		: 	tuple(numeric, numeric), optional(default=None)
						Provide a Prodution breakdown
	"""
	def __init__(self, name, products, technology):
		self.name = name
		self.products = products
		self.technology = technology

	def __str__(self):
		return "%s" % self.name

	def output(self, quantities):
		"""
		Provide Quantities of Labour to understand Country Output

		Parameters
		----------
		quantities 	: 	tuple(numeric, numeric)
		"""
		self.quantities = quantities
		self.output = (quantities[0] / self.technology[0] , quantities[1] / self.technology[1])
		return self.output

class TradeSystem(object):
	"""
	Constructs a Trading System of Countries and Products to Compute Trade Outcomes
	"""
	def __init__(self, countries):
		self.countries = []
		for country in countries:
			print "Adding: %s" % country.name
			self.countries.append(country.name)
			#-Set Each Country as an Attribute-#
			setattr(self, "%s"%country, country)

	@property
	def output(self):
		output = []
		for country in self.countries:
			output.append(getattr(self, country).output)
		p1 = output[0][0] + output[1][0]
		p2 = output[0][1] + output[1][1]
		return (p1,p2)


if __name__ == "__main__":
	#-Construct Country Objects-#
	england = Country(name="England", products=('Wine', 'Cloth'), technology=(120, 100))
	portugal = Country(name="Portugal", products=('Wine', 'Cloth'), technology=(80, 90))
	system = TradeSystem(countries=[england, portugal])

	#-Absolute Output-#
	print england.output((1000,1000))
	print portugal.output((1000,1000))

	print system.output



