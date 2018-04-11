Python SDK for DataHub.io
=========================

[TOC]

## User stories

Data-curator and programmer stories:

1. I want **to load** the data from the DataHub into my program so I can
    - analyze data records
    - build graphics
    - update data, print data, etc
```python
package = datahub.open('wordbank/gold-prices')
print(package.resources)
[
    {name: "global", path: "...", format: "csv"},
    {name: "europe", path: "...", format: "csv"}
]
print(package.resources[0].rows())
'''
date, price
2001, 389
2002, 354
...
```
2. I want **to dump** the data on the disk/zip/database, so I can
    - work with the data using local programs
    - create a local cache\backup
```python
package = datahub.open('finances/finance-vix')
package.dump('finance-vix')
os.system('tree ./finance-vix')
'''
./finance-vix/
├── archive
│   └── vix-daily.csv
├── data
│   ├── validation_report.json
│   ├── vix-daily_csv.csv
│   └── vix-daily_json.json
├── datapackage.json
└── README.md
```
3. I want to **store** data (e.g. prices) online and to **share** data with other people or use it with other programs:
```python
price_list = Package.open('shop/prices/datapackage.json')
link, version = datahub.push(package)

# update your users, upload into a e-shop, whatever
letter = 'Our prices was updated: %s' % link
clients_list = DB.users(status='subcontractor')
mail_server.send(letter, clients_list)
```
4. I want to **have a versioning** of my data on the DataHub, so I can
    - **get previous version** (I'm not scared to break the data)
```python
package = datahub.open('myname/mydata')
if check_my_data_function(package.resources[0]) == 'invalid':
    version = package.descriptor.version - 1
    package = datahub.open('myname/mydata/%s' % version)
```
5. I want to have a search API, so I can find the data by the keyword or author's name.
```python
global_warming = datahub.search('global warming by UN')

for dataset in global_warming:
    if datetime(dataset.descriptor.updated) > datetime.year(2015):
        dataset.dump(path=dataset.descriptor.name)
```

## Datahub python lib

This future lib is called **"datahub-py"**.

We also have a JS `datahub-client` library already, that was extracted from the `data-cli` program. 
`Datahub-client` represents the JS interface to the DataHub, but in fact it is a bunch of `data-cli` modules, and has no elegant structure.
Thus, the new `datahub-py` lib will be not just a copy of `datahub-client`, but designed from scratch and take some of the js lib features.

### Composition
`Datahub-py` will include two main classes:
- **`DataHub`** class to handle the interactions with our server
- **`Package`** class from https://github.com/frictionlessdata/datapackage-py, that represents a dataset. Original `Package` class will be extended with `dump()` method.

**Note:** *Datapackage, dataset, package* - all this words often means the same - data file(s) plus the 'descriptor' file, that contains meta-information. See [dataset specification](https://frictionlessdata.io/docs/data-package/).
`Package` class .



### Features to support
- [ ] authorization (private data, ownership)
- [ ] load/open the dataset from the DataHub
- [ ] dump the dataset
- [ ] push the dataset onto the DataHub
    - have different versions
- [ ] init a new dataset or update an existing
    * non-interactive by default
- [ ] search through datasets by:
    - keywords 
    - author | organization
    - findability
- [ ] validate schema & data in the dataset
    * check the dataset, loaded from disk/created by user/other program
    * validate schema/data before pushing on the DataHub

### not to support
- info - should be implemented in the end user app, all the info is easy to get from the dataset object
- cat: should be implemented in the end user app, too


# `Datahub-py` Tutorial

## DataHub class

```python
from datahub import DataHub
```

### Authentication

The existing DataHub auth using secure JWT tokens and is easy to use in the lib.
User will take the API key from his publishers page ('Copy API key' button or 'Settings' page, or something..).

User will provide the key once on the __init__() stage and forget handling AUTH in other methods:
```python
datahub = DataHub('Your API key is here.')

# hmmmm, what about something like this?
print(datahub.user)
'''
{name: 'John',
 avatar: 'URL',
 userId: '1032847018327',
...}
'''
# could be useful for multiuser scenario
```

Current Login mechanism, used in the JS lib, is too complex and includes running local web-server and opening a Browser window, which is not applicable in the library (but could be implemented in the end app, if needed)

### Open Package from the DataHub

```python
'''arguments
source: datasetID:   [owner/]package[/version_index]
            (by default: owner=current_user; version=latest)
        URL on the DataHub:     http://datahub.io/core/gdp/[v/10]
        descriptor url:         http://datahub.io/core/gdp/datapackage.json
'''
dataset = datahub.open(source='...')
```

This method is a wrapper around **`dataset = Package('datapackage.json')`**, but also handles:
- links which are not pointing to `dp.json`, e.g. https://datahub.io/core/gdp
- **auth** for private datasets

### Push a package to DataHub server

I decided to keep the method simple:
```python
# loading data
dataset = Package('...')

# set/check metadata, validation, etc
# ...

'Pushing on the DataHub:'
URL, version = datahub.push(dataset)
# output: Tuple
('http://datahub.io/owner/dataset_name/', 1)
```

### Init a new package

`Datahub.init()` could use `Package.infer()`;
Please consider that `init()` should be non-interactive by default.
See https://github.com/datahq/datahub-qa/issues/178 from Rufus:
> * [ ] make init non-interactive by default and add option --interactive or > -i for interactive mode
>   * [ ] guess name from directory name
>   * [ ] use name to generate title
>   * [ ] set license to ODC attribution or PDDL (?)
>   * [ ] (?) Use readme to set description
>* [ ] decide which fields to auto create for the user e.g.
>   * [ ] licenses
>   * [ ] sources (?)
>* [ ] prompt for title first and then auto-suggest name from title (or use directory name for title?)


```python
'''Args:
path: - to file
      - to folder
interactive: True|False
'''
dataset = datahub.init(path='...', interactive=False)

# check/modify dataset.descriptor, schema, add sources, etc
# ...

# dataset.dump(),
# Datahub.push(dataset),
# ...
```
When the folder already contains `datapackage.json`, the `init()` method should update only the missing info (e.g. new files).
Existing metadata like **`name, title, description, etc`** should stay untouched.

### Search

```python
datahub.search('key words OR author OR unlisted|private|published')
'List [dataset1, dataset2, dataset3, ...]'

# we could also split args in this method:
datahub.search(keywords='...', author='...', findability='...')
```
The output should return lazy objects (dataset's metadata like 'readme' is loaded when called). Datasets (except zipped), stored on the DataHub, have remote resource files, stored on AWS, so the resources are lazy by default.
That is one more reason for implementing `Package.dump()`.

### Validate

#### User Stories:
1. I want to validate records that my program created/loaded, so I know it is correct
2. `DataHub.push()` will use Validation before pushing data on the server, to save the time and the bandwidth.

#### What we already have
1. `Package` has `valid()` getter, that checks if the Schema (not the data!) is valid:
```python
dataset = Package('http://datahub.io/core/gdp')
print(dataset.valid) # True|False
print(dataset.errors)  # list of errors, if any
```
2. `Tableschema-py` checks the data records against the schema, when reading the table:
```python
table = Table('data.csv')
table.read(keyed=True)
# [<ValidationError: "explanation text">]
```
3. `Tableschema-py` also could validate the schema: `table.schema.valid # false`.

#### Validation in our lib
For our purposes we could make a wrapper to combine existing features into one method:
```python
dataset = Package('...')
valid, errors = datahub.validate(dataset)
# output:
'True|False', [list of tableschema errors]
```

But also we could extend the `Package` class, so it also will validate the data records:
```python
dataset = Package('...')

# change something (schema, data, etc)

dataset.valid  # True if the schema AND DATA records is valid
dataset.error  # list of the errors or Null
```

## Extended `Package` class

### Dump a dataset to the folder/file/database:

`Package.save()` method saves only local data files.
Datasets from the DataHub has remote resources, so we need to implement method, that will fetch and save all remote resources:
```python
dataset = datahub.open('...')

'''dump arguments
target:  folder path - save files+descriptor in the folder
         file.zip path - save all in the archive
         file.json        - save descriptor + data inline?
         file-like object - save descriptor + data inline?
storage: invoke `Package.save(storage=...)` method
'''
dataset.dump(target='path[.zip|.json]', storage=None)
```

We can PullRequest this method directly into `datapackage-py` lib. It is useful for other people, too.

### Validate

See the section in the `DataHub` class: [Validate](#Validate)
