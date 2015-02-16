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
		self.exchange_rate = self.technology[0] / self.technology[1]

	def __str__(self):
		return "%s" % self.name

	@property
	def output(self):
		""" 
		Return Computed Output
		Requires Technology and Quantity Information
		"""
		return (self.quantities[0] / self.technology[0] , self.quantities[1] / self.technology[1])

	def set_quantities(self, quantities):
		""" Set Quantities Vector """
		self.quantities = quantities

	def difference_quantities(self, differences):
		""" 
		Provide Differences to Quantities of One Product

		Assumption: Full Employment

		Tuple(Product, Difference in Production Quantity)

		"""
		try:
			quantities = getattr(self, quantities)
		except:
			self.quantities = (0,0) 											#Not Set Yet and may want to use differences only
		product = differences[0]
		if product == 0:
			q0 = self.quantities[0] + differences[1]
			q1 = self.quantities[1] + -1 * differences[1] * self.exchange_rate
			self.quantities = (q0, q1)
		if product == 1:
			q0 = self.quantities[0] + -1 * differences[1] * 1 / self.exchange_rate
			q1 = self.quantities[1] + differences[1]
			self.quantities = (q0, q1)

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

	def __str__(self):
		return "TradeSystem (Wine: %s; Cloth: %s)" % (self.quantities[0], self.quantities[1])

	@property 
	def quantities(self):
		quantities = []
		for country in self.countries:
			quantities.append(getattr(self, country).quantities)
		q1 = quantities[0][0] + quantities[1][0]
		q2 = quantities[0][1] + quantities[1][1]
		return (q1,q2)

	@property
	def output(self):
		output = []
		for country in self.countries:
			output.append(getattr(self, country).output)
		o1 = output[0][0] + output[1][0]
		o2 = output[0][1] + output[1][1]
		return (o1,o2)


if __name__ == "__main__":
	#-Construct Country Objects-#
	england = Country(name="England", products=('Wine', 'Cloth'), technology=(120, 100))
	portugal = Country(name="Portugal", products=('Wine', 'Cloth'), technology=(80, 90))
	system = TradeSystem(countries=[england, portugal])

	#-Differences in Output => In Line with Comparative Advantage-#
	england.difference_quantities((0,-5))
	print england.quantities
	portugal.difference_quantities((0,6.75))
	print portugal.quantities
	print system

	#-Differences in Output => Not in line with Comparative Advantage-#
	england.difference_quantities((0,5))
	print england.quantities
	portugal.difference_quantities((0,-5))
	print portugal.quantities
	print system


