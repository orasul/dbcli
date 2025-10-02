dbcli provides lightweight utilities set for basic CRUD operations for MongoDB and Redis.
rcli provides similar interface for Redis DB. You are able to edit strings(bytes), lists and hashs with json-like syntax in your text editor.


# dbcli

[![PyPI version](https://badge.fury.io/py/dbcli-mongo-redis.svg)](https://badge.fury.io/py/dbcli-mongo-redis)
[![Downloads](https://pepy.tech/badge/dbcli-mongo-redis)](https://pepy.tech/project/dbcli-mongo-redis)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

**dbcli** is a set of lightweight CLI utilities for basic CRUD operations with MongoDB and Redis using your favorite text editor.

## Features
- Fast editing and viewing of MongoDB documents and Redis data
- Uses $EDITOR (or notepad for Windows) for interactive editing
- Document validation before saving
- Supports strings, lists, and hashes in Redis

## Requirements
- Python 3.7+
- [pymongo](https://pymongo.readthedocs.io/en/stable/) (for mcli)
- [redis-py](https://github.com/redis/redis-py) (for rcli)

## Installation

```bash
pip install dbcli-mongo-redis
```

## Quick Start

```bash
# List MongoDB databases
mcli list-dbs
# List Redis keys
rcli list-keys
```

## CLI Utilities
- **mcli** — MongoDB client based on pymongo
- **rcli** — Redis client based on redis-py

## Installation

``` bash
pip install dbcli-mongo-redis
```


---


---

### mcli usage examples (MongoDB)

```bash
# List all databases (short and long key)
mcli list-dbs
# List collections in the 'books' database
mcli list-cols -d books
mcli list-cols --database books
# List documents in the 'authors' collection
mcli -d books -c authors list-docs
mcli --database books --collection authors list-docs
# Filter documents by field
mcli -d books -c authors list-docs -f '{"Language":"Chinese"}'
mcli --database books --collection authors list-docs --filter '{"Language":"Chinese"}'
# Show document by id
mcli -d aws -c images show-doc -i ami-eede2314
mcli --database aws --collection images show-doc --document-id ami-eede2314
# Show document by ObjectId
mcli -d gcloud -c elements show-doc -o 5ef869cf316dd267c64be59c
mcli --database gcloud --collection elements show-doc --document-object-id 5ef869cf316dd267c64be59c
# Edit document
mcli -d devops -c newcol edit-doc -o 5ef865fceb8e7562e8eaf9f6
mcli --database devops --collection newcol edit-doc --document-object-id 5ef865fceb8e7562e8eaf9f6
# Delete document
mcli -d devops -c newcol del-doc -i object-234
mcli --database devops --collection newcol del-doc --document-id object-234
```



### rcli usage examples (Redis)

```bash
# Count keys in the database
rcli db-count
# List all keys
rcli list-keys
# List keys by prefix (short and long key)
rcli list-keys -p image
rcli list-keys --prefix image
# Show database contents
rcli show-db
# Show value by key (short and long key)
rcli show-db -k image_325
rcli show-db --key image_325
# Add and edit data
rcli add-key
rcli add-key --type hash
rcli edit-doc -k image_325
rcli edit-doc --key image_325
# Delete key
rcli del-doc -k image_214
rcli del-doc --key image_214
# Convert types
rcli to-set -k some_list
rcli to-set --key some_list
rcli to-zset -k some_hash
rcli to-zset --key some_hash
```

---


## Limitations

**Not recommended for production or for bulk updates!**
This tool is intended for interactive work with small amounts of data.

---



## Contributing

Pull requests are welcome! Please open issues for bugs and feature requests.

## Links
- [PyPI](https://pypi.org/project/dbcli-mongo-redis/)
- [pymongo documentation](https://pymongo.readthedocs.io/en/stable/)
- [redis-py documentation](https://redis-py.readthedocs.io/en/stable/)
- Inspired by [dbcli.com](https://www.dbcli.com)

---


## License & Authors

- Authors: Rasul Osmanov, Artur Krasnykh

```text
Copyright (c) 2020, Rasul Osmanov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```



## TODO
```text
- AWS DynamoDB client
- Google Cloud DataStore client
```
