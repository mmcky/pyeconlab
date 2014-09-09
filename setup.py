"""
Setup File for PyEconLab

Future Work
-----------
[1] Add Install Dependancies
"""

from distutils.core import setup

setup(
  name = 'pyeconlab',
  packages = [ 'pyeconlab',
               'pyeconlab.country',
  			       'pyeconlab.util',
  			       'pyeconlab.trade',
  			       'pyeconlab.trade.dataset',
               'pyeconlab.trade.dataset.CEPIIBACI',
               'pyeconlab.trade.dataset.CEPIIBACI.meta',          #Really?
               'pyeconlab.trade.dataset.NBERFeenstraWTF',
               'pyeconlab.trade.dataset.NBERFeenstraWTF.meta',    #Really?
               'pyeconlab.trade.classification',
               'pyeconlab.trade.concordance',
               'pyeconlab.trade.systems',
  			       'pyeconlab.wdi',
  			  ], 
  package_data =  { 'pyeconlab.country' : ['data/*.xls', 'data/*.xml'],
                    'pyeconlab.trade.dataset.CEPIIBACI.meta' : ['meta/*.py', 'meta/curated/*.csv'],
                    'pyeconlab.trade.dataset.NBERFeenstraWTF' : ['data/*.py'],
                    'pyeconlab.trade.dataset.NBERFeenstraWTF.meta' : ['meta/*.py', 'meta/csv/*.csv'],
                    'pyeconlab.trade.classification'  :   ['data/un/*.txt', 'data/wits/*.xls'],  
                  },
  version = '0.1-alpha',
  description = 'Python Package For Economists',
  author = 'Matthew McKay',
  author_email = 'mamckay@gmail.com',
  url = 'https://github.com/sanguineturtle/pyeconlab',
  download_url = 'https://github.com/sanguineturtle/pyeconlab/tarball/0.1-alpha', 
  keywords = ['quantitative', 'economics', 'international trade', 'complexity'],
  #install_requires = ['countrycode', 'rarfile'],
)
