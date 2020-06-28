# dbcli
DataBase cli utilities
* mcli - Mongo client based on pymongo
* rcli - Redis client based on pymongo

#### mcli usage examples
``` bash
mcli list-dbs
mcli list-cols -d books
mcli list-docs -d books -c authors
mcli show-doc -d aws -c images -i ami-eede2314
mcli show-doc --database aws --collection images -i ami-eede2314
mcli show-doc --database aws --collection images --document-id ami-eede2314
mcli show-doc -d gcloud -c elements -o 5ef869cf316dd267c64be59c
mcli show-doc -d gcloud -c elements --document-object-id 5ef869cf316dd267c64be59c
mcli edit-doc -d devops -c newcol -o 5ef865fceb8e7562e8eaf9f6
mcli edit-doc -d devops -c newcol -i object-234
```

Inspired by [dbcli](https://www.dbcli.com).

## Limitations

Should avoid using in production and for huge amount of data.


## License & Authors

- Author:: Rasul Osmanov

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
