from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dbcli_mongo_redis",
    version="0.3.4",
    description="Mongo and redis cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orasul/dbcli",
    packages=find_packages(),
    author="Rasul Osmanov",
    install_requires=["click", "flatten_json", "pymongo", "redis"],
    entry_points={
        "console_scripts": [
            "rcli = dbcli.rcli:_main",
            "mcli = dbcli.mcli:_main",
        ],
    },
    include_package_data=True,
)
