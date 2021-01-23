#!/usr/bin/env python3
import json

import click
import redis

js_edit_opts = {"require_save": False, "extension": ".js"}


def multiple_add(cl, edited_doc):
    data = json.loads(edited_doc)
    with cl.pipeline() as pipe:
        for key, value in data.items():
            if isinstance(value, dict):
                pipe.hmset(key, value)
            elif isinstance(value, list):
                pipe.rpush(key, *value)
            else:
                pipe.set(key, value)
        pipe.execute()


def add_any_key_type(cl, edited_doc, key_type, key):
    data = json.loads(edited_doc)
    if key_type == "string":
        cl.set(key, data)
    elif key_type == "bits":
        cl.setbit(key, data["offset"], data["value"])
    elif key_type == "list":
        cl.rpush(key, *data)
    elif key_type == "hash":
        cl.hmset(key, data)
    elif key_type == "set":
        cl.sadd(key, *data)
    elif key_type == "zset":
        try:
            cl.zadd(key, data)
        except AttributeError:
            dct = {}
            for item in data:
                dct[item[0]] = item[1]
            cl.zadd(key, dct)
    elif key_type == "hyll":
        cl.pfadd(key, *data)


def bytes_to_string(structure):
    new_dct = {}

    def a(data):
        if isinstance(data, (list, set, tuple)):
            res_list = []
            for item in data:
                if isinstance(item, (set, list, tuple, dict)):
                    res_list.append(a(item))
                else:
                    if isinstance(item, float):
                        res_list.append(item)
                    else:
                        res_list.append(item.decode("utf-8"))
            return res_list
        elif isinstance(data, dict):
            dct = {}
            for key, value in data.items():
                dct[key.decode("utf-8")] = a(value)
            return dct
        else:
            return data.decode("utf-8")

    for key, value in structure.items():
        new_dct[key.decode("utf-8")] = a(value)
    return new_dct


@click.group()
@click.option("-h", "--host", default="localhost", help="Redis host.")
@click.option("-p", "--port", default=6379, help="Redis port.")
@click.option("-d", "--db", default=0, help="Database number.")
@click.pass_context
def cli(ctx, host, port, db):
    """Redis client based on redis-py \n
    Usage ex: \n
        rcli list-keys \n
        rcli list-keys -p image \n
        rcli show-db \n
        rcli show-db -p image_ \n
        rcli add-key key_name \n
        rcli add-key key_name [-h|-s|-l|-z|-e|-b] \n
        rcli add-data
        rcli edit-doc image_325 \n
        rcli del-key image_214 \n
        rcli to-set some_list \n
        rcli to-zset some_hash \n

    """
    ctx.ensure_object(dict)
    ctx.obj["RedisClient"] = redis.Redis(host=host, port=port, db=db)
    return ctx.obj["RedisClient"]


@cli.command()
@click.pass_context
def db_count():
    """Show count of db."""
    cl = redis.StrictRedis()
    print(cl.config_get("databases"))


@cli.command()
@click.option("-p", "--pattern", default="*", help="Keys search pattern.")
@click.pass_context
def list_keys(ctx, pattern):
    """Show all keys in db(uft-8 format)."""
    cl = ctx.obj["RedisClient"]
    keys = [key.decode("utf-8") for key in cl.keys(pattern=(pattern + "*"))]
    print(*keys, sep="\n")


@cli.command()
@click.option("-k", "--key", default=None, help="Document key.")
@click.option("-p", "--pattern", default="*", help="Keys search pattern.")
@click.pass_context
def show_db(ctx, key, pattern):
    """Show data in 'key: value' format."""
    cl = ctx.obj["RedisClient"]
    if key:
        keys_list = [key.encode("utf-8")]
    else:
        keys_list = cl.keys(pattern=pattern)
    # check key type and get key's value
    for key in keys_list:
        if cl.type(key) == b"string":
            print(key, ": ", cl.get(key))
        elif cl.type(key) == b"hash":
            print(key, ": ", cl.hgetall(key))
        elif cl.type(key) == b"list":
            print(key, ": ", cl.lrange(key, 0, -1))
        elif cl.type(key) == b"set":
            print(key, ": ", cl.smembers(key))
        elif cl.type(key) == b"zset":
            print(key, ": ", cl.zrange(key, 0, -1, withscores=True))
        else:
            print("Unsupported value in key: ", key)


@cli.command()
@click.argument("key")
@click.option("-b", "--bits/--no-bits", default=False, help="Bits type key")
@click.option("-l", "--lst/--no-lst", default=False, help="List type key")
@click.option("-h", "--hsh/--no-hsh", default=False, help="Hash type key")
@click.option("-s", "--st/--no-st", default=False, help="Set type key")
@click.option("-z", "--zst/--no-zst", default=False, help="Sorted set type key")
@click.option("-e", "--hyll/--no-hyll", default=False, help="HyperLogLog type key")
@click.pass_context
def add_key(ctx, key, bits, lst, hsh, st, zst, hyll):
    """Add key to db. Don't support streams and geo."""
    cl = ctx.obj["RedisClient"]
    key_type = None
    types_dict = {
        "bits": bits,
        "list": lst,
        "set": st,
        "hash": hsh,
        "zset": zst,
        "hyll": hyll,
    }
    for ke, value in types_dict.items():
        if value:
            if key_type is None:
                key_type = ke
            else:
                raise click.ClickException("Only one key type can be set")
    if key_type is None:
        key_type = "string"
    if key_type == "string":
        new_doc = "value"
    elif key_type == "list":
        new_doc = ["value1", "value2", "value3"]
    elif key_type == "set":
        new_doc = ["value1", "value2", "value3"]
    elif key_type == "bits":
        new_doc = {"offset": 1, "value": 1}
    elif key_type == "zset":
        new_doc = {"key1": 1.1, "key2": 1.2}
    elif key_type == "hash":
        new_doc = {"key1": "value1", "key2": "value2"}
    elif key_type == "hyll":
        new_doc = ["1", "2", "3", "4"]
    else:
        print(key_type)
        raise click.ClickException("Key type should be set")
    edited_doc = click.edit(json.dumps(new_doc, indent=4), **js_edit_opts)
    if edited_doc:
        try:
            add_any_key_type(cl, edited_doc, key_type, key)
        except Exception as ex:
            print("Key was not added: ", ex)


@cli.command()
@click.pass_context
def add_data(ctx):
    """Add json-format data to db. Multiple keys can be added."""
    cl = ctx.obj["RedisClient"]
    new_doc = {"key1": "value1", "key2": "value2"}
    edited_doc = click.edit(json.dumps(new_doc, indent=4), **js_edit_opts)
    if edited_doc:
        try:
            multiple_add(cl, edited_doc)
        except Exception as ex:
            print("Key was not added: ", ex)


@cli.command()
@click.argument("key")
@click.pass_context
def edit_doc(ctx, key):
    """Open document in editor. Support only json-format.

    KEY: key of the document"""
    cl = ctx.obj["RedisClient"]
    if cl.type(key) == b"string":
        key_type = "string"
        try:
            new_doc = {key: cl.get(key).decode("utf-8")}
        except UnicodeDecodeError:
            raise click.ClickException("HyperLogLog cant be edited")
    elif cl.type(key) == b"list":
        key_type = "list"
        new_doc = bytes_to_string({key.encode("utf-8"): cl.lrange(key, 0, -1)})
    elif cl.type(key) == b"set":
        key_type = "set"
        new_doc = bytes_to_string({key.encode("utf-8"): cl.smembers(key)})
    elif cl.type(key) == b"hash":
        key_type = "hash"
        new_doc = bytes_to_string({key.encode("utf-8"): cl.hgetall(key)})
    elif cl.type(key) == b"zset":
        key_type = "zset"
        new_doc = bytes_to_string(
            {key.encode("utf-8"): cl.zrange(key, 0, -1, withscores=True)}
        )
    else:
        raise click.ClickException(
            f'Wrong key: "{key}" or unsupported key type: "{cl.type(key)}"'
        )
    edited_doc = click.edit(
        json.dumps(new_doc, indent=4), require_save=True, extension=".js"
    )
    if edited_doc:
        try:
            new_key = [*json.loads(edited_doc).keys()]
            if len(new_key) != 1:
                raise click.ClickException("Only one key can be edited at a time")
            cl.delete(key)
            add_any_key_type(
                cl, json.dumps(json.loads(edited_doc)[new_key[0]]), key_type, new_key[0]
            )
        except Exception as ex:
            print("Key was not edited: ", ex)
            add_any_key_type(cl, json.dumps(new_doc[key]), key_type, key)


@cli.command()
@click.argument("key")
@click.pass_context
def del_key(ctx, key):
    """Delete key from db."""
    cl = ctx.obj["RedisClient"]
    cl.delete(key)


@cli.command()
@click.argument("key")
@click.pass_context
def to_set(ctx, key):
    """Turn redis list to set."""
    cl = ctx.obj["RedisClient"]
    if cl.type(key) == b"list":
        data = cl.lrange(key, 0, -1)
        cl.delete(key)
        cl.sadd(key, *data)
    else:
        raise click.ClickException(
            f'Wrong key type: "{cl.type(key)}". Argument should be b"list"'
        )


@cli.command()
@click.argument("key")
@click.pass_context
def to_zset(ctx, key):
    """Turn redis hash into sorted set."""
    cl = ctx.obj["RedisClient"]
    if cl.type(key) == b"hash":
        data = cl.hgetall(key)
        try:
            cl.delete(key)
            cl.zadd(key, data)
        except Exception:
            cl.hmset(key, data)
            print(f"Wrong value in key: {data}")
    else:
        raise click.ClickException(
            f'Wrong key type: "{cl.type(key)}". Argument should be b"hash"'
        )


def _main():
    cli(obj={})


if __name__ == "__main__":
    _main()
