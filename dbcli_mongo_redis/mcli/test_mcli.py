import click
import pymongo
from bson.objectid import ObjectId
from click.testing import CliRunner
from mock import Mock

from dbcli_mongo_redis.mcli.mcli import cli

m = pymongo.MongoClient(host="localhost", port=27017)
m.drop_database("mcli_db_test")
db = m["mcli_db_test"]
coll = db["first"]

runner = CliRunner()


def get_data():
    val = coll.find({})
    data = []
    for item in val:
        data.append(item)
    return data


def test_add_to_db():
    click.edit = Mock(return_value='{"_id": "123",' '"key1": "value1"}')
    runner.invoke(cli, ["-d", "mcli_db_test", "-c", "first", "add-doc"])
    click.edit = Mock(return_value='{"key2": "value3"}')
    runner.invoke(cli, ["-d", "mcli_db_test", "-c", "first", "add-doc"])
    val = coll.find({})
    data = []
    for item in val:
        data.append(item)

    assert data[0] == {"_id": "123", "key1": "value1"}
    assert data[1] == {"_id": ObjectId(f'{data[1]["_id"]}'), "key2": "value3"}


def test_show_doc_with_id_and_objectid():
    data = get_data()
    result1 = runner.invoke(
        cli, ["-d", "mcli_db_test", "-c", "first", "show-doc", "-o", data[1]["_id"]]
    )
    result2 = runner.invoke(
        cli, ["-d", "mcli_db_test", "-c", "first", "show-doc", "-i", data[0]["_id"]]
    )

    assert (
        result1.stdout == "{\n    "
        f'"_id": "{data[1]["_id"]}",\n    '
        '"key2": "value3"\n'
        "}\n"
    )
    assert result2.stdout == "{\n    " '"_id": "123",\n    ' '"key1": "value1"\n' "}\n"


def test_edit_doc():
    click.edit = Mock(return_value='{"_id": "123",' '"new_key1": "new_value1"}')
    runner.invoke(cli, ["-d", "mcli_db_test", "-c", "first", "edit-doc", "-i", "123"])

    data = get_data()

    assert data[0] == {"_id": "123", "new_key1": "new_value1"}


def test_delete_doc():
    runner.invoke(cli, ["-d", "mcli_db_test", "-c", "first", "del-doc", "-i", "123"])

    assert coll.find_one("{_id: 123}") is None
