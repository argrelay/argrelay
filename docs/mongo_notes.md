


Download Mongo DB and Shell from: https://www.mongodb.com/try/download/community
*   `mongodb-linux-x86_64-rhel80-6.0.3.tgz`
*   `mongosh-1.6.1-linux-x64.tgz`


Start server:

```sh
~/argrelay.git/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/Works/argrelay.git/mongodb/data
```

Start client:

```sh
~/argrelay.git/mongo/mongosh-1.6.1-linux-x64/bin/mongosh
```

Client: configure username and password:
https://stackoverflow.com/questions/38921414/mongodb-what-are-the-default-user-and-password/38921949#38921949

```
use admin
db.createUser(
   {
     user: "test",
     pwd: passwordPrompt(), // or cleartext password
     roles: [ 
       { role: "userAdminAnyDatabase", db: "admin" },
       { role: "readWriteAnyDatabase", db: "admin" } 
     ]
   }
)
```

Tutorial:
https://www.mongodb.com/languages/python

Installing python client:

```sh
python -m pip install "pymongo[srv]"
```

Run:
* pymongo_get_database.py
* pymongo_test_insert.py

From MongoDB shell exploring collections:

```
show databases # has `some_database`
use some_database
show collections # has `some_collection`

# Use collection `some_collection` to list all its items:
db.some_collection.find()
```
