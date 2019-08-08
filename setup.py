from setuptools import setup

setup(name='networks-cleaning',
	version='1.0',
	packages=['locationmatching', 'namematching','registrationreconfigure'],
	#scripts=['usermodules/shared/scripts/utils.py','usermodules/shared/scripts/connections.py'],
	install_requires=[
		'numpy>=1.14',
		'pandas>=0.22',
		'tqdm>=4.31',
		'fuzzywuzzy==0.17.0'
		#'python-dateutil==2.8.0',
		#'xlrd==1.2.0'
	],
	package_dir={'':'usermodules'},
	entry_points={
		'console_scripts': [
			'locationmatching = locationmatching.__main__:main',
			'registrationreconfigure = registrationreconfigure.__main__:main',
			'namematching = namematching.__main__:main',
		]
	},
)
