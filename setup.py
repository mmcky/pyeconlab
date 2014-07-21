from distutils.core import setup

setup(
  name = 'pyeconlab',
  packages = [ 'pyeconlab',
  			       'pyeconlab.util',
  			       'pyeconlab.trade',
  			       'pyeconlab.trade.dataset',
               'pyeconlab.trade.dataset.NBERFeenstraWTF',
  			       'pyeconlab.wdi',
  			  ], 
  version = '0.1-alpha',
  description = 'Python Package For Economists',
  author = 'Matthew McKay',
  author_email = 'mamckay@gmail.com',
  url = 'https://github.com/sanguineturtle/pyeconlab',
  download_url = 'https://github.com/sanguineturtle/pyeconlab/tarball/0.1-alpha', 
  keywords = ['quantitative', 'economics', 'international trade', 'complexity'] 
)
