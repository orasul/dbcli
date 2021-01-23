from setuptools import setup


setup(name='dbcli_mongo_redis',
      version='0.3.1',
      description='Mongo and redis cli',
      url='https://github.com/orasul/dbcli',
      packages=['dbcli_mongo_redis.mcli', 'dbcli_mongo_redis.rcli'],
      author='Rasul Osmanov',
      install_requires=[
          'click',
          'flatten_json',
          'pymongo',
          'redis'
      ],
      entry_points={
          'console_scripts': [
              'rcli = dbcli_mongo_redis.rcli.rcli:_main',
              'mcli = dbcli_mongo_redis.mcli.mcli:_main',
          ],
      },
      include_package_data=True)