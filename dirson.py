"""Encode/decode JSON-like structure to directory.

    +-------------------+---------------+
    | Python            | JSON          |
    +===================+===============+
    | dict, namedtuple  | object        |
    +-------------------+---------------+
    | list, tuple       | array         |
    +-------------------+---------------+
    | str, unicode      | string        |
    +-------------------+---------------+
    | int, long, float  | number        |
    +-------------------+---------------+
    | True              | true          |
    +-------------------+---------------+
    | False             | false         |
    +-------------------+---------------+
    | None              | null          |
    +-------------------+---------------+

Quickstart
----------

>>> import dirson
>>> from pygit2 import init_repository
>>> repo = init_repository('/tmp/storage', bare=True)
>>> dirson.encode(repo, {'a': {'b': 1}})
>>> tree = repo.index.write_tree()
>>> parent = [] if repo.head_is_unborn else repo.head.target
>>> first_commit = repo.create_commit(
...     'refs/heads/master',
...     dirson.signature,
...     dirson.signature,
...     tree,
...     parent)

Load ``HEAD`` as index:

>>> repo.index.read_tree(repo[repo.head.target].tree)

"""

import os
import json

import click
import pygit2

__version__ = "0.1.0.dev20180111"


signature = pygit2.Signature(
    'DirSON',
    'jiri.kuncar+dirson@gmail.com'
)


def _from_obj(obj):
    """Yield tuples with path and item."""
    stack = [([], obj)]

    while stack:
        path, item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                stack.insert(0, (path + ['"{0}"'.format(key)], value))
        elif isinstance(item, (tuple, list)):
            for key, value in enumerate(item):
                stack.insert(0, (path + [str(key)], value))
        else:
            yield path, item


def _entry(repo, path, item):
    """Create an instance of ``IndexEntry``."""
    return pygit2.IndexEntry(
        '/'.join(path),
        repo.create_blob(json.dumps(item)),
        pygit2.GIT_FILEMODE_BLOB,
    )


def encode(repo, data, index=None):
    """Update index with new data and removes unused ones."""
    paths = set()
    index = repo.index if index is None else index
    for path, item in _from_obj(data):
        index_entry = _entry(repo, path, item)
        for existing_entry in index:
            if existing_entry.path.startswith(index_entry.path):
                index.remove(existing_entry.path)
        index.add(index_entry)
        paths.add(index_entry.path)

    remove = set(index_entry.path for index_entry in index) - paths
    for path in remove:
        index.remove(path)

    # index.write()
    return index


def _path_defaults(path):
    """Yield path defaults."""
    for key in path:
        yield json.loads(key)


def decode(repo, index=None):
    """Decode index to a Python structure."""
    index = repo.index if index is None else index
    result = None

    for index_entry in index:
        parts = list(_path_defaults(index_entry.path.split('/')))

        key = parts[0]
        if result is None:
            result = [] if isinstance(key, int) else {}

        branch = result
        for next_key in parts[1:]:
            if isinstance(key, int):
                try:
                    branch = branch[key]
                except IndexError:
                    branch.extend((
                        [] if isinstance(next_key, int) else {}
                        for i in range(1 + key - len(branch))
                    ))
                    branch = branch[key]
            else:
                branch = branch.setdefault(
                    key,
                    [] if isinstance(next_key, int) else {}
                )
            key = next_key

        key = parts[-1]
        value = json.loads(repo[index_entry.id].data)
        if isinstance(key, int):
            branch.insert(key, value)
        else:
            branch[key] = json.loads(repo[index_entry.id].data)

    return result


@click.group()
def cli():
    """DirSON command line interface."""


@cli.command()
@click.option('--source', type=click.File('r'), default='-')
def smudge(source):
    """Load a JSON object from Git to file."""
    info = list(source.readlines())
    tree_id = info[1].split(':')[1].strip()

    repo = pygit2.Repository(os.getcwd())
    tree = repo[tree_id]
    index = pygit2.Index()
    index.read_tree(tree)

    data = json.dumps(decode(repo, index=index))
    assert int(info[2].split(' ')[1].strip()) == len(data)
    click.echo(data)


@cli.command()
@click.option('--source', type=click.File('rb'), default='-')
def clean(source):
    """Store a JSON file in Git repository."""
    repo = pygit2.Repository(os.getcwd())
    data = json.load(source)
    index = encode(
        repo,
        data,
        # index=pygit2.Index(),
    )
    index.write()
    tree_id = index.write_tree(repo)
    click.echo(
        "version https://github.com/jirikuncar/dirson/v1\n"
        "oid sha1:{tree_id}\n"
        "size {size}".format(tree_id=tree_id, size=len(json.dumps(data))))
