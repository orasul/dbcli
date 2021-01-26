#!/usr/bin/env python3
import json

import click
import redis

js_edit_opts = {"require_save": False, "extension": ".js"}


def multiple_add(cl, edited_doc):
    data = json.loads(edited_doc)
    with cl.pipeline() as pipe:
        # set value to key depends on type of value
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
    append_func = {
        "string": cl.set,
        "list": cl.rpush,
        "hash": cl.hmset,
        "set": cl.sadd,
        "zset": cl.zadd,
        "hyll": cl.pfadd,
    }
    if key_type in ["string", "hash", "zset"]:
        try:
            append_func[key_type](key, data)
        except AttributeError:
            # if value list of tuples/list turns it to dict
            dct = {}
            for item in data:
                dct[item[0]] = item[1]
            append_func[key_type](key, dct)
    elif key_type in ["list", "set", "hyll"]:
        append_func[key_type](key, *data)
    elif key_type == "bits":
        cl.setbit(key, data["offset"], data["value"])


def b_to_str(structure):
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
    """Redis client based on redis-py"""
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
    type_dct = {b"string": cl.get, b"set": cl.smembers, b"hash": cl.hgetall}
    for key in keys_list:
        if cl.type(key) in type_dct:
            print(key, ": ", type_dct[cl.type(key)](key))
        elif cl.type(key) == b"list":
            print(key, ": ", cl.lrange(key, 0, -1))
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
@click.option("-z", "--zst/--no-zst", default=False, help="Zset type key")
@click.option("-e", "--hyll/--no-hyll", default=False, help="HyLL type key")
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
    # Check for multiple types incoming
    for ke, value in types_dict.items():
        if value:
            if key_type is None:
                key_type = ke
            else:
                raise click.ClickException("Only one key type can be set")
    new_value_dct = {
        "string": "value",
        "list": ["value1", "value2", "value3"],
        "set": ["value1", "value2", "value3"],
        "bits": {"offset": 1, "value": 1},
        "zset": {"key1": 1.1, "key2": 1.2},
        "hash": {"key1": "value1", "key2": "value2"},
        "hyll": ["1", "2", "3", "4"],
    }
    # set type of key to key_type
    if key_type is None:
        key_type = "string"
    if key_type in new_value_dct:
        new_doc = new_value_dct[key_type]
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
    type_dct = {
        b"string": ["string", cl.get],
        b"set": ["set", cl.smembers],
        b"hash": ["hash", cl.hgetall],
    }
    # set type to key_type and get key's value
    k_type = cl.type(key)
    if k_type in type_dct:
        key_type = type_dct[k_type][0]
        try:
            new_doc = b_to_str({key.encode("utf-8"): type_dct[k_type][1](key)})
        except UnicodeDecodeError:
            raise click.ClickException("HyperLogLog cant be edited")
    elif k_type == b"list":
        key_type = "list"
        new_doc = b_to_str({key.encode("utf-8"): cl.lrange(key, 0, -1)})
    elif k_type == b"zset":
        key_type = "zset"
        new_doc = b_to_str(
            {key.encode("utf-8"): cl.zrange(key, 0, -1, withscores=True)}
        )
    else:
        raise click.ClickException(
            f'Wrong key: "{key}" or unsupported key type: "{k_type}"'
        )
    edited_doc = click.edit(
        json.dumps(new_doc, indent=4), require_save=True, extension=".js"
    )
    if edited_doc:
        try:
            # get key name (in case of changing)
            new_key = [*json.loads(edited_doc).keys()]
            # check for multiple keys
            if len(new_key) != 1:
                raise click.ClickException("Only one key can be edited")
            cl.delete(key)
            data = json.loads(edited_doc)[new_key[0]]
            add_any_key_type(cl, json.dumps(data), key_type, new_key[0])
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
    # get key's value and set with new type
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
    # get key's value and set with new type
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
