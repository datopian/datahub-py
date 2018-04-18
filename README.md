Python SDK for DataHub
=======================

**Status - On Hold:**
- The API design is 80-90% finished on @Dima's mind
- But this doc takes too much time
- and the lib implementation will take even more
- also we'll need to update the server-side API to support the features we want to see here.

Issue: https://github.com/datahq/pm/issues/137


General Feedback from @Adam:
- +1 user story for you to fill in. (done)
- think “how users would use API”, not “what API needs to do”
- just mirroring the server APIs to Python methods is NOT helpful to users.
- Doing user stories is a good exercise for understanding which APIs are actually needed and how they should look like.
- telling direct answers is not a good teaching
- confusing use of the terms **package, dataset, datapackage** interchangeably.
> I remember I was confused with the question **"what's the diff between dataset, datapackage, `datapackage.json`?"**, too
>
> **package, dataset, datapackage** terms are used interchangeably in the dev-chat and datahub.io docs.
>
> So I use all of them with intend to make users get used with all three terms, and I left a Note about *"these three is the same and here is the specification of data-package"*.
>
> If you are not agree with that - I'll fix this doc.
> [name=Dima]
- same name (Package) for the original `datapackage-py` class and for the derived one is confusing.
> 1. I think the `datahub.Package` should be independent from the `datahub.DataHub`
>    `datahub.Package` methods should NOT use the datahub.io API
> 2. Ideally I would backport the new features (init, validate, dump) back to the original `datapackage-py` repo.
> 3. so in the end `datahub.Package` will be just a link to `datapackage.Package`
> 3. Also I cannot invent the proper name for `datahub.Package`:
>     - `DataPackage` - we already have the `datapackage` repo
>     - `DataSet` - says nothing special
>     - `DataHubPackage` - may be this?
> 3. But if the `datahub.Package` class will evolve into some kind of ORM, e.g.
> ```python
> Package.resource.change_data_method()
> Package.commit()  # save the changes on the DataHub remotely
> ```
> Then of course we should separate `datahub.Package` and `datapackage.Package` more obviously.

[[toc]]

## User stories

Let's say I'm a guy, who works with data.
My programs scraps and generate megabytes of useful data every day.

Once I meet a DataHub site in the internet. I'm now exited about its ideas.
Now I want to store all my data on the datahub and to use datahub as a source of data, too.

So I've learned the data-package concept and I tried to use `data-cli` tool for my needs.
However `Data-cli` doesn't satisfy me completely. Reasons are:
- It is not fully automatic
- My server has no GUI, so I can't run the browser to authorize
- I want to automate uploading and sharing my data
- I want to use datasets from the datahub directly in my programs

So I found this SDK and I want to write a script(s) that will do all work for me:
- store my data online.
    - organize and describe my data (create a dataset).
    - check if the data is valid
    - upload it
- share uploaded data with my colleagues.
- search data:
    - find my own datasets on the datahub later.
    - find other useful datasets on the datahub
- open the data from the datahub to use it in my programs

## Use case #1: create, upload, share

### 1. I want to organize my data, add description, ...
so I can:
    - my customers know what is the data about
    - I have a standard data-package to use with existing Frictionless libs.
```python
from datahub import Package

dataset = Package.init('mydata/folder')  # grab all files, README, LICENSE etc

# in original datapackage.Package it looks like this:
dataset = Package()
for file in folder.files:
    dataset.add_resource(file)

# now I can add meta information
dataset.descriptor.description = "bla bla bla"
```

### 2. I want to validate my data, so I'm sure it is correct
```python
'''extended Package class'''
from datahub import Package

package = Package('mydata/datapackage.json')
valid, errors = package.validate()  # (True, [])

'''or like this:'''
package.valid   # True|False
package.errors  # list of errors if any
```

### 3. Now (after creating and validating) I want to put my dataset online

```python
price_list = Package.open('shop/prices/datapackage.json')
uploaded_price = datahub.push(package)
print(uploaded_price.descriptor)
{
    'datahub': {'created': datetime_object,
             'findability': 'published',
             'flowid': 'username/packagename/11',  # last number is the version
             'hash': '9875382f45701d2860d94965f4272074',
             'owner': 'username',
             'ownerid': 'userId',
             'stats': {'bytes': 83482, 'rowcount': 817}},
    'description': '....',
    'id': 'username/packagename',
...}
```

> ^ why not `price_list.push()`? [name=Adam]
> Because `Package` class knows nothing about the DataHub server and its interfaces.
>    it is the `DataHub` class who interacts with the server.

### 4. Now I can share a link to my data:

```python
letter = 'Our prices was updated: http://datahub.io/' + \
         uploaded_price.descriptor[id]

clients_list = DB.users(status='subcontractor')
mail_server.send(letter, clients_list)
```

## Use case #2: find, load and dump

### 5. I want to find the data by the keyword or author's name.

```python
datahub.search('key words, author name')
# returns  List[dataset1, dataset2, dataset3, ...]

# You could also filter search results by author and/or findability
datahub.search(keywords='...', owner='...', findability='...')
```

```python
global_warming = datahub.search('global warming by UN')

for dataset in global_warming:
    if datetime(dataset.descriptor.updated) > datetime.year(2015):
        dataset.dump(path=dataset.descriptor.name)
```

### 6. I want **to load** the data from the DataHub into my program
so I can
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

### 7. I want to **have a versioning** of my data on the DataHub

so I can **get previous version** and not scared to break the data.

> @dima - is version currently part of the descriptor? [name=Adam]
> No, but I think we are going to implement it:
> - versioning is in our userstories here: https://docs.datahub.io/developers/user-stories/#5-versioning-and-changes-in-data-packages
> - a user requested (I created issue) to implement versioning

```python
package = datahub.open('myname/mydata')
if check_my_data_function(package.resources[0]) == 'invalid':
    version = package.descriptor.version - 1
    package = datahub.open('myname/mydata/%s' % version)
```

### 8. I want **to dump** the data on the disk/zip/database

So I can:
- work with the data using my programs (e.g. excel)
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

## Use case #3 - load, change, upload, share

I want to write a script that does the following:
- Loads a core dataset from the datahub
- Iterate on all rows, for each row adds a new field with a computed value
- The result is uploaded to datahub under my user
- After it's up, I want to send the json link to another online service (e.g. use it in an API).

### solution #1 - immutable
Assume that Data-package, loaded from the datahub, is immutable (reasons: 1. user is not the owner, 2. resource is remote).

> I'm not happy with this long code listing... but it should work with existing `datapackage.Package` lib.
In **Solution #2** I've tried to imaging a better API [name=Dima]


#### 1. load data from the datahub
```python
from datahub import DataHub
datahub_client = DataHub('my api key')

# load the gold history prices
gold_prices = datahub_client.open('core/gold-prices')
gold_data = gold_prices.get_resource('data_csv')
gold_headers = price_table.headers

# load the euro history prices
euro_price = datahub_client.open('exchange_history/euro')
euro_data = euro_price.get_resource('data_csv')
# transform euro prices into dict: {date:price}
euro_price_history = {date: price for (date, price) in euro_data}
# {'2001': 1.01,
#  '2002': 1.02,
#   etc...}
```

#### 2. iterate on all rows and add new field

I decided to use a file on the disk for storing new generated data.
Probably I could create the `tableschema.Table` instance in the memory, fill it and then convent into a resource, but our future user is not experienced frictionless-data guy.
```python

with open('gold_prices.csv', 'w') as file:
    my_headers = gold_headers + ['price in euro']
    print(*my_headers, sep=',', file=file)

    # Iterating:
    for date, gold_price_in_dollar in gold_data.read():
        euro_to_dollar_rate = euro_price_history[date]
        gold_price_in_euro = price * euro_to_dollar_rate

        print(date, gold_price_in_dollar, gold_price_in_euro, sep=',', file=file)
```

#### 3. create a new package and upload the result
```python
from datahub import Package, Resource

# creating a new DataPackage
my_gold_prices = Package()

# copying the metadata
my_gold_prices.descriptor = gold_prices.descriptor
my_gold_prices.descriptor.description = my_gold_prices.descriptor.description + \
    'Added a column with the gold price in euro.'

# delete original resource
my_gold_prices.remove_resource('data_csv')

# add the new resource
my_resource = Resource({'path': 'gold_prices.csv'})
my_resource.infer()
my_gold_prices.add_resource(my_resource.descriptor)

# upload perfoms under the user credentials (inferred from the api_key)
uploaded_dataset = datahub.push(my_gold_prices)
```

#### 4. share data with other service

```python
import requests

link_to_share = 'https://datahub.io/' + uploaded_dataset.descriptor['id']
# 'https://datahub.io/username/gold-prices'


data = {
    'message': 'new data arrived.',
    'link': link_to_share
}
res = requests.post('http://mynewsserver.com/api/', data=data)
```

### solution #2 - mutable resources

What if we have extended the `datapackage.Resource` class, and `Resource` is mutable now:
```python
euro_prices = datahub.open('exchange-rates/euro')
# transform euro prices into dict.
euro_price_history = {date: price for (date, price)
                      in euro_price.get_resource('data_csv')}

gold_prices = datahub.open('core/gold-prices')
gold_data = gold_prices.get_resource('data_csv')

# Update the resource
gold_data.headers.append('price in euro')
for record in gold_data.iter():  # record = [date, price]
    date, price_usd = record
    price_euro = euro_price_history[date] * price_usd
    record.append(price_euro)

# probably the resource.descriptor won't update automatically
# so we can infer it again ?
gold_data.infer()
# OR implement: gold_data.update_descriptor() ???
```
Then user can upload and share the updated data-set as described above.


# Datahub python module

Our future lib is called **"datahub-py"**.

We also have a JS `datahub-client` library already, that was extracted from the `data-cli` program.
`Datahub-client` represents the JS interface to the DataHub, but in fact it is a bunch of `data-cli` modules, and has no elegant structure.
Thus, the new `datahub-py` lib will be not just a copy of `datahub-client`, but designed from scratch and take some of the js lib features.

### Composition
`Datahub-py` will include two main classes:
- **`DataHub`** class to handle the interactions with our server
    - `__init__()` also authenticate user
    - `push()`
    - `search()`
    - `open()`
- **`Package`** class that represents a dataset. Original https://github.com/frictionlessdata/datapackage-py `Package` class extended with
    -  `init()`
    -  `validate()`
    -  `dump()`

**Note:** *Datapackage, dataset, package* - all this words often means the same - data file(s) plus the 'descriptor' file, that contains meta-information. See [dataset specification](https://frictionlessdata.io/docs/data-package/).

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

'Pushing on the DataHub creates a new dataset with remote resources (which are stored on the datahub server)'
uploaded_dataset = datahub.push(dataset)
```

If you need to push a separate file you need to convert it into a dataset first:
```python
dataset = datahub.init('data.csv')
uploaded_dataset = datahub.push(dataset)
```

### Search

```python
datahub.search('key words, author name')
# returns  List[dataset1, dataset2, dataset3, ...]

# You could also filter search results by author and/or findability
datahub.search(keywords='...', owner='...', findability='...')
```

The output should return lazy objects (dataset's metadata like 'readme' is loaded when called). Datasets (except zipped), stored on the DataHub, have remote resource files, stored on AWS, so the resources are lazy by default.
That is one more reason for implementing `Package.dump()`.


## Extended `Package` class

### Init a new package

`Package.init()` could use `Package.infer()`;
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
dataset = Package.init(path='...', interactive=False)

# check/modify dataset.descriptor, schema, add sources, etc
# ...

# dataset.dump(),
# Datahub.push(dataset),
# ...
```
When the folder already contains `datapackage.json`, the `init()` method should update only the missing info (e.g. new files).
Existing metadata like **`name, title, description, etc`** should stay untouched.

### Validate

#### User Stories:
1. I want to validate records that my program created/loaded, so I know it is correct
2. `DataHub.push()` will use Validation before pushing data on the server, to save the time and the bandwidth.

#### What we already have
1. `Package` has `valid()` getter, that checks if the Schema (not the data!) is valid:
```python
dataset = Package('datapackage.json')
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

#### Implementing validation in our lib:

For our purposes we could make a wrapper to combine existing features and extend the `Package` class, so it also will validate the data records:
```python
'''extended Package class'''
from datahub import Package

dataset = Package.init('path')

# change something (schema, data, etc)

valid, errors = dataset.validate()  # (True, [])

'''or like this:'''
dataset.valid  # True if the schema AND DATA records is valid
dataset.error  # errors list
```


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
The method could also return a data-package with dumped resources.
