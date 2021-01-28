#!/usr/bin/env python3
import datetime
import json

import click
import flatten_json
import pymongo
from bson.json_util import dumps, loads
from bson.objectid import ObjectId


# From json.dump documentation: If specified, default should be a function
# that gets called for objects that can’t otherwise be serialized. It should
# return a JSON encodable version of the object or raise a TypeError. If not
# specified, TypeError is raised.
def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, ObjectId):
        return str(x)
    else:
        raise TypeError(x)


js_opts = {"require_save": False, "extension": ".json"}


@click.group()
@click.option("-h", "--host", default="localhost", help="MongoDB host.")
@click.option("-p", "--port", default=27017, help="MongoDB port.")
@click.option("-d", "--database", default=False, help="Database name.")
@click.option("-c", "--collection", help="Collection.")
@click.pass_context
def cli(ctx, host, port, database, collection):
    """Mongo client based on pymongo"""
    ctx.ensure_object(dict)
    cl = pymongo.MongoClient(host=host, port=port)
    if database and collection:
        db = cl[database]
        ctx.obj["Collection"] = db[collection]
    if database:
        ctx.obj["Database"] = cl[database]
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
@click.pass_context
def list_cols(ctx):
    """List collections in DB"""
    try:
        db = ctx.obj["Database"]
    except KeyError:
        raise click.ClickException("Database name should be set")
    cols = db.list_collections()
    for col in cols:
        print(col["name"])


@cli.command()
@click.option("-f", "--filter", default="{}", help="Filter json.")
@click.pass_context
def list_docs(ctx, filter):
    """List document ids from collection"""
    try:
        coll = ctx.obj["Collection"]
    except KeyError:
        raise click.ClickException("Both collection and db name should be set")
    filter = json.loads(filter)
    data = coll.find(filter)
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
    try:
        coll = ctx.obj["Collection"]
    except KeyError:
        raise click.ClickException("Both collection and db name should be set")
    # make filter using id or object_id
    if document_id:
        filter = {"_id": document_id}
    elif document_object_id:
        filter = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    data = coll.find_one(filter)
    # print result using flatten json format
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
    try:
        coll = ctx.obj["Collection"]
    except KeyError:
        raise click.ClickException("Both collection and db name should be set")
    new_doc = {"title": "titlename", "key1": "value1", "key2": "value2"}
    edited_doc = click.edit(json.dumps(new_doc, indent=4), **js_opts)
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
    try:
        coll = ctx.obj["Collection"]
    except KeyError:
        raise click.ClickException("Both collection and db name should be set")
    # make filter using id or object_id
    if document_id:
        filt = {"_id": document_id}
    elif document_object_id:
        filt = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    data = coll.find_one(filt)
    if data:
        dumped_obj = json.loads(dumps(data))
        edited_doc = click.edit(json.dumps(dumped_obj, indent=4), **js_opts)
    else:
        raise click.ClickException("No document with this id or ObjectId")
    if edited_doc:
        try:
            coll.replace_one(filt, loads(edited_doc))
        except Exception as ex:
            print("Json?", ex)


@cli.command()
@click.option("-i", "--document-id", help="Document _id value.")
@click.option("-o", "--document-object-id", help="Document ObjectId value.")
@click.pass_context
def del_doc(ctx, document_id, document_object_id):
    """Delete document from db"""
    try:
        coll = ctx.obj["Collection"]
    except KeyError:
        raise click.ClickException("Both collection and db name should be set")
    # make filter using id or object_id
    if document_id:
        filt = {"_id": document_id}
    elif document_object_id:
        filt = {"_id": ObjectId(document_object_id)}
    else:
        raise click.ClickException(
            "Either --document-object-id or\
                            --document-id should be set"
        )
    coll.delete_one(filt)


def _main():
    cli(obj={})


if __name__ == "__main__":
    _main()
