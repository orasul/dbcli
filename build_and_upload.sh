#!/bin/bash

# Clean old build data
rm -rf build/ dbcli_mongo_redis.egg-info/ dist/

# 
python3 setup.py sdist bdist_wheel

#
python3 -m twine upload --repository pypi dist/*


