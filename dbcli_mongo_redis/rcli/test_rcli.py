import click
import redis
from click.testing import CliRunner
from mock import Mock

from dbcli_mongo_redis.rcli.rcli import cli

r = redis.Redis()
r.flushdb()
runner = CliRunner()


def test_add_to_db():
    click.edit = Mock(
        return_value='{"key1": "value1",'
        '"key2": {"key21": "value21", "key22": "value22"},'
        '"key3": ["value31", "value32"]}'
    )
    runner.invoke(cli, "add-data")

    assert r.get("key1") == b"value1"
    assert r.hgetall("key2") == {b"key21": b"value21", b"key22": b"value22"}
    assert r.lrange("key3", 0, -1) == [b"value31", b"value32"]


def test_edit_doc():
    click.edit = Mock(return_value='{"key1": "val1"}')
    runner.invoke(cli, ["edit-doc", "key1"])
    click.edit = Mock(return_value='{"key2": {"key21": "val21"}}')
    runner.invoke(cli, ["edit-doc", "key2"])
    click.edit = Mock(return_value='{"key3": ["val31", "val32"]}')
    runner.invoke(cli, ["edit-doc", "key3"])

    assert r.get("key1") == b"val1"
    assert r.hgetall("key2") == {b"key21": b"val21"}
    assert r.lrange("key3", 0, -1) == [b"val31", b"val32"]


def test_show_db_with_pattern_and_with_key():
    result1 = runner.invoke(cli, ["show-db", "-p", "key*"])
    result2 = runner.invoke(cli, ["show-db", "-k", "key1"])

    assert (
        result1.stdout == "b'key3' :  [b'val31', b'val32']\n"
        "b'key2' :  {b'key21': b'val21'}\n"
        "b'key1' :  b'val1'\n"
    )
    assert result2.stdout == "b'key1' :  b'val1'\n"


def test_list_to_set():
    runner.invoke(cli, ["to-set", "key3"])
    assert r.type("key3") == b"set"


def test_hash_to_zset():
    r.hmset("sset", {"key41": 1.1, "key42": 1.0})
    runner.invoke(cli, ["to-zset", "sset"])

    assert r.type("sset") == b"zset"


def test_delete_doc():
    r.set("some_key", "some_value")
    runner.invoke(cli, ["del-doc", "some_key"])

    assert r.get("some_key") is None
