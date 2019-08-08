from setuptools import setup

setup(name='networks-cleaning',
	version='1.0',
	packages=[''],
	scripts=['usermodules/shared/scripts/utils.py','usermodules/shared/scripts/connections.py'],
	install_requires=[
		'numpy>=1.14,<1.15',
		'pandas>=0.22,<0.23',
		'tqdm>=4.31',
		'fuzzywuzzy==0.17.0'
	],
	package_dir={'':'usermodules'},
	entry_points={
		'console_scripts': [
			'checkdata = checkdata.__main__:main',
			'prephrms = prephrms.__main__:main',
			'updateemployees = updateemployees.__main__:main',
			'getupdates = getupdates.__main__:main',
			'uploaddiary = uploaddiary.__main__:main',
			'uploaduid = uploaduid.__main__:main',
			'processupdates = processupdates.__main__:main',
			'resetuser = resetuser.__main__:main',
			'createstateuser = createstateuser.__main__:main',
			'notifyusers = notifyusers.__main__:main',
			'updateofficers = updateofficers.__main__:main',
		]
	},
)
