# dbcli
DataBase cli utilities
* mcli - Mongo client based on pymongo
* rcli - Redis client based on pyredis

#### mcli usage examples
``` bash
mcli list-dbs
mcli list-cols -d books
mcli -d books -c authors list-docs
mcli -d aws -c images show-doc -i ami-eede2314
mcli --database aws --collection images show-doc -i ami-eede2314
mcli --database aws --collection images show-doc --document-id ami-eede2314
mcli -d gcloud -c elements show-doc -o 5ef869cf316dd267c64be59c
mcli -d gcloud -c elements show-doc --document-object-id 5ef869cf316dd267c64be59c
mcli -d devops -c newcol edit-doc -o 5ef865fceb8e7562e8eaf9f6
mcli -d devops -c newcol edit-doc  -i object-234
mcli -d devops -c newcol del-doc -i object-234
mcli -d devops -c newcol del-doc -o 5ef865fceb8e7562e8eaf9f6
```

#### rcli usage examples
```bash
rcli db-count
rcli list-keys
rcli list-keys -p image
rcli show-db
rcli show-db -k image_325
rcli show-db -p image_
rcli add-data
rcli add-key
rcli add-key -t hash
rcli edit-doc -k image_325
rcli del-doc -k image_214
rcli to-set -k some_list
rcli to-zset -k some_hash
```
Inspired by [dbcli](https://www.dbcli.com).

## Limitations

Should avoid using in production and for huge amount of data.


## License & Authors

- Authors:: Rasul Osmanov, Artur Krasnykh

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
