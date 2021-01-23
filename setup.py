from setuptools import setup, find_packages


setup(name='dbcli',
      version='0.3.1',
      description='Mongo and redis cli',
      url='https://github.com/orasul/dbcli',
      packages=find_packages(),
      author='Rasul Osmanov',
      install_requires=[
          'click',
          'flatten_json',
          'pymongo',
          'redis'
      ],
      entry_points={
          'console_scripts': [
              'rcli = dbcli.rcli:_main',
              'mcli = dbcli.mcli:_main',
          ],
      },
      include_package_data=True)