#!/usr/bin/env python3

import click
import pymongo
import json
import datetime
from bson.objectid import ObjectId
import flatten_json
from bson.json_util import dumps, loads


def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, ObjectId):
        return str(x)
    else:
        raise TypeError(x)


@click.group()
@click.option('-h', '--host', default='localhost', help='MongoDB host.')
@click.option('-p', '--port', default=27017, help='MongoDB port.')
@click.pass_context
def cli(ctx, host, port):
    ctx.ensure_object(dict)
    ctx.obj['MongoClient'] = pymongo.MongoClient(host=host, port=port)


@cli.command()
@click.pass_context
def list_dbs(ctx):
    """List databases in Mongo"""
    cl = ctx.obj['MongoClient']
    dbs = cl.list_databases()
    for db in dbs:
        print(db["name"])


@cli.command()
@click.option('-d', '--database', help='Database name.')
@click.pass_context
def list_cols(ctx, database):
    """List collections in DB"""
    cl = ctx.obj['MongoClient']
    db = cl[database]
    cols = db.list_collections()
    for col in cols:
        print(col["name"])


@cli.command()
@click.option('-d', '--database', help='Database name.')
@click.option('-c', '--collection', help='Collection.')
@click.option('-f', '--filter', 'filt', default='{}', help='Filter json.')
@click.pass_context
def list_docs(ctx, database, collection, filt):
    """List document ids from collection"""
    cl = ctx.obj['MongoClient']
    db = cl[database]
    coll = db[collection]
    filt = json.loads(filt)
    data = coll.find(filt)
    for doc in data:
        if isinstance(doc["_id"], ObjectId):
            print("ObjectId: ", end="")
        print(doc["_id"])


@cli.command()
@click.option('-d', '--database', help='Database name.')
@click.option('-c', '--collection', help='Collection.')
@click.option('-i', '--document-id', help='Document _id value.')
@click.option('-o', '--document-object-id', help='Document ObjectId value.')
@click.option('-f', '--flatten/--no-flatten', default=False)
@click.pass_context
def show_doc(ctx, database, collection, document_id, document_object_id, flatten):
    """Show document by id"""
    cl = ctx.obj['MongoClient']
    db = cl[database]
    coll = db[collection]
    if document_id:
        filt = '{'+f'"_id":"{document_id}"'+'}'
        filt = json.loads(filt)
    elif document_object_id:
        filt = {'_id': ObjectId(document_object_id)}
    else:
        raise RuntimeError("Either --document-object-id or --document-id should be set")
    data = coll.find_one(filt)
    if flatten:
        data = flatten_json.flatten_json(data)
        for k, v in data.items():
            print(f'{k}: {v}')
    else:
        print(json.dumps(data, indent=4, default=json_handler))


@cli.command()
@click.option('-d', '--database', help='Database name.')
@click.option('-c', '--collection', help='Collection.')
@click.pass_context
def add_doc(ctx, database, collection):
    """Add document to collection"""
    cl = ctx.obj['MongoClient']
    db = cl[database]
    coll = db[collection]
    edit_json = {'title': 'titlename', 'key1': 'value1', 'key2': 'value2'}
    edited_document = click.edit(json.dumps(edit_json, indent=4), require_save=True, extension='.json')
    if edited_document:
        try:
            data = json.loads(edited_document)
            print(json.dumps(data, indent=4, default=json_handler))
            inserted_id = coll.insert(data)
            print(f'Inserted ObjectId: {inserted_id}')
        except Exception as ex:
            print('Json?', ex)


@cli.command()
@click.option('-d', '--database', help='Database name.')
@click.option('-c', '--collection', help='Collection.')
@click.option('-i', '--document-id', help='Document _id value.')
@click.option('-o', '--document-object-id', help='Document ObjectId value.')
@click.pass_context
def edit_doc(ctx, database, collection, document_id, document_object_id):
    """Edit document"""
    cl = ctx.obj['MongoClient']
    db = cl[database]
    collection = db[collection]
    if document_id:
        filt = '{'+f'"_id":"{document_id}"'+'}'
        filt = json.loads(filt)
    elif document_object_id:
        filt = {'_id': ObjectId(document_object_id)}
    else:
        raise RuntimeError("Either --document-object-id or --document-id should be set")
    data = collection.find_one(filt)
    dumped_object = json.loads(dumps(data))
    edited_document = click.edit(json.dumps(dumped_object, indent=4), require_save=True, extension='.json')
    if edited_document:
        try:
            collection.replace_one(filt, loads(edited_document))
        except Exception as ex:
            print('Json?', ex)


if __name__ == '__main__':
    cli(obj={})
