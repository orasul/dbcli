#!/usr/bin/env python3
import datetime
import json

import click
import flatten_json
import pymongo
from bson.json_util import dumps, loads
from bson.objectid import ObjectId


def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, ObjectId):
        return str(x)
    else:
        raise TypeError(x)


js_edit_opts = {"require_save": False, "extension": ".json"}


@click.group()
@click.option("-h", "--host", default="localhost", help="MongoDB host.")
@click.option("-p", "--port", default=27017, help="MongoDB port.")
@click.option("-d", "--database", default=False, help="Database name.")
@click.option("-c", "--collection", help="Collection.")
@click.pass_context
def cli(ctx, host, port, database, collection):
    """Mongo client based on pymongo \n
    mcli usage examples: \n
    mcli list-dbs \n
    mcli list-cols -d books \n
    mcli -d books -c authors list-docs \n
    mcli -d aws -c images show-doc -i ami-eede2314 \n
    mcli --database aws --collection images show-doc -i ami-eede2314 \n
    mcli --database aws --collection images show-doc --document-id ami-eede2314 \n
    mcli -d gcloud -c elements show-doc -o 5ef869cf316dd267c64be59c \n
    mcli -d gcloud -c elements show-doc --document-object-id 5ef869cf316dd267c64be59c \n
    mcli -d devops -c newcol edit-doc -o 5ef865fceb8e7562e8eaf9f6 \n
    mcli -d devops -c newcol edit-doc  -i object-234 \n
    mcli -d devops -c newcol del-doc -i object-234 \n
    mcli -d devops -c newcol del-doc -o 5ef865fceb8e7562e8eaf9f6 \n

    """
    ctx.ensure_object(dict)
    cl = pymongo.MongoClient(host=host, port=port)
    if database and collection:
        db = cl[database]
        ctx.obj["Collection"] = db[collection]
    else:
        raise click.ClickException("Database and collection should be set")
    ctx.obj["MongoClient"] = cl


@cli.command()
@click.pass_context
def list_dbs(ctx):
    """List databases in Mongo"""
    cl = ctx.obj["MongoClient"]
    dbs = cl.list_databases()
    for db in dbs:
        print(db["name"])


@cli.command()
@click.option("-d", "--database", help="Database name.")
@click.pass_context
def list_cols(ctx, database):
    """List collections in DB"""
    cl = ctx.obj["MongoClient"]
    db = cl[database]
    cols = db.list_collections()
    for col in cols:
        print(col["name"])


@cli.command()
@click.option("-f", "--filter", "filt", default="{}", help="Filter json.")
@click.pass_context
def list_docs(ctx, filt):
    """List document ids from collection"""
    coll = ctx.obj["Collection"]
    filt = json.loads(filt)
    data = coll.find(filt)
    for doc in data:
        if isinstance(doc["_id"], ObjectId):
            print("ObjectId: ", end="")
        print(doc["_id"])


@cli.command()
@click.option("-i", "--document-id", help="Document _id value.")
@click.option("-o", "--document-object-id", help="Document ObjectId value.")
@click.option("-f", "--flatten/--no-flatten", default=False)
@click.pass_context
def show_doc(ctx, document_id, document_object_id, flatten):
    """Show document by id"""
    coll = ctx.obj["Collection"]
    # make filter using id or object_id
    if document_id:
        filt = "{" + f'"_id":"{document_id}"' + "}"
        filt = json.loads(filt)
    elif document_object_id:
        filt = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    data = coll.find_one(filt)
    if flatten:
        if data:
            data = flatten_json.flatten_json(data)
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            raise click.ClickException("No document with this id or ObjectId")
    else:
        print(json.dumps(data, indent=4, default=json_handler))


@cli.command()
@click.pass_context
def add_doc(ctx):
    """Add document to collection"""
    coll = ctx.obj["Collection"]
    new_doc = {"title": "titlename", "key1": "value1", "key2": "value2"}
    edited_doc = click.edit(json.dumps(new_doc, indent=4), **js_edit_opts)
    # insert json-format data into db
    if edited_doc:
        try:
            data = json.loads(edited_doc)
            print(json.dumps(data, indent=4, default=json_handler))
            inserted_id = coll.insert(data)
            print(f"Inserted ObjectId: {inserted_id}")
        except Exception as ex:
            print("Json?", ex)


@cli.command()
@click.option("-i", "--document-id", help="Document _id value.")
@click.option("-o", "--document-object-id", help="Document ObjectId value.")
@click.pass_context
def edit_doc(ctx, document_id, document_object_id):
    """Edit document"""
    collection = ctx.obj["Collection"]
    # make filter using id or object_id
    if document_id:
        filt = "{" + f'"_id":"{document_id}"' + "}"
        filt = json.loads(filt)
    elif document_object_id:
        filt = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    data = collection.find_one(filt)
    if data:
        dumped_obj = json.loads(dumps(data))
        edited_doc = click.edit(json.dumps(dumped_obj, indent=4), **js_edit_opts)
    else:
        raise click.ClickException("No document with this id or ObjectId")
    if edited_doc:
        try:
            collection.replace_one(filt, loads(edited_doc))
        except Exception as ex:
            print("Json?", ex)


@cli.command()
@click.option("-i", "--document-id", help="Document _id value.")
@click.option("-o", "--document-object-id", help="Document ObjectId value.")
@click.pass_context
def del_doc(ctx, document_id, document_object_id):
    """Delete document from db"""
    collection = ctx.obj["Collection"]
    if document_id:
        filt = "{" + f'"_id":"{document_id}"' + "}"
        filt = json.loads(filt)
    elif document_object_id:
        filt = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    collection.delete_one(filt)


def _main():
    cli(obj={})


if __name__ == "__main__":
    _main()
