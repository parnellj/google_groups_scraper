try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'name': 'Google Groups Scraper',
	'version': '0.1',
	'url': 'https://github.com/parnellj/PLACEHOLDER_NAME',
	'download_url': 'https://github.com/parnellj/PLACEHOLDER_NAME',
	'author': 'Justin Parnell',
	'author_email': 'parnell.justin@gmail.com',
	'maintainer': 'Justin Parnell',
	'maintainer_email': 'parnell.justin@gmail.com',
	'classifiers': [],
	'license': 'GNU GPL v3.0',
	'description': 'A tool for scraping thread titles and posts (articles) from historical Google Groups Usenet archives.',
	'long_description': 'A tool for scraping thread titles and posts (articles) from historical Google Groups Usenet archives.',
	'keywords': '',
	'install_requires': ['nose'],
	'packages': ['PLACEHOLDER_NAME'],
	'scripts': []
}
	
setup(**config)