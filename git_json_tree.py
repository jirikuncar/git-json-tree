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

>>> import git_json_tree
>>> from dulwich.repo import Repo
>>> repo = Repo('/tmp/storage')
>>> tree_id = git_json_tree.encode(repo, {'a': {'b': 1}})
>>> git_json_tree.decode(repo, tree_id)
{'a': {'b': 1}}

"""

import json
import os
import stat
import warnings

import click
from dulwich.index import pathjoin, pathsplit
from dulwich.objects import Blob, Tree
from dulwich.repo import Repo

__version__ = "0.1.0.dev20180121"

GIT_FILEMODE_BLOB = 33188


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


def encode(repo, data):
    """Create new tree in a repo."""
    trees = {b'': {}}

    def add_tree(path):
        if path in trees:
            return trees[path]
        dirname, basename = pathsplit(path)
        t = add_tree(dirname)
        assert isinstance(basename, bytes)
        newtree = {}
        t[basename] = newtree
        trees[path] = newtree
        return newtree

    for path, item in _from_obj(data):
        tree_path = '/'.join(path[:-1]).encode('utf-8')
        basename = path[-1].encode('utf-8')
        tree = add_tree(tree_path)

        blob = Blob.from_string(json.dumps(item).encode('utf-8'))
        repo.object_store.add_object(blob)

        tree[basename] = (GIT_FILEMODE_BLOB, blob.id)

    def build_tree(path):
        tree = Tree()
        for basename, entry in trees[path].items():
            if isinstance(entry, dict):
                mode = stat.S_IFDIR
                sha = build_tree(pathjoin(path, basename))
            else:
                (mode, sha) = entry
            tree.add(basename, mode, sha)
        repo.object_store.add_object(tree)
        return tree.id

    return build_tree(b'')


def _path_defaults(path):
    """Yield path defaults."""
    for key in path:
        yield json.loads(key)


def decode(repo, tree_id):
    """Decode index to a Python structure."""
    tree = repo[tree_id]

    if tree.type_name == b'tree':
        items = [(json.loads(item.path, encoding='utf-8'), item.sha)
                 for item in tree.items()]
        if all((isinstance(key[0], str) for key in items)):
            return {key: decode(repo, sha) for key, sha in items}
        elif all((isinstance(key[0], int) for key in items)):
            items = ((int(key), decode(repo, sha)) for key, sha in items)
            return [item[1] for item in sorted(items)]

        raise TypeError('Mixed values in: {0}'.format(tree))

    elif tree.type_name == b'blob':
        return json.loads(tree.data, encoding='utf-8')

    elif tree.type_name == b'commit':
        return decode(repo, tree.tree)

    import ipdb
    ipdb.set_trace()

    raise TypeError('Invalid object: {0}'.format(tree))


@click.group()
def cli():
    """git-json-tree command line interface."""


@cli.command(name='encode')
@click.option('--source', type=click.File('rb'), default='-')
@click.option('--git', type=click.Path(exists=True), default='.')
def cli_encode(source, git):
    """Encode a JSON object in a Git tree."""
    click.echo(encode(Repo(git), json.load(source)))


@cli.command(name='decode')
@click.argument('oid', default='HEAD')
@click.option('--git', type=click.Path(exists=True), default='.')
def cli_decode(oid, git):
    """Decode a Git tree to a JSON object."""
    click.echo(json.dumps(decode(Repo(git), oid.encode('utf-8'))))


@cli.command()
@click.option('--source', type=click.File('rb'), default='-')
@click.option('--git', type=click.Path(exists=True), default='.')
def smudge(source, git):
    """Load a JSON object from Git to file."""
    info = list(source.readlines())
    tree_id = info[1].split(b':')[1].strip()

    repo = Repo(git)
    data = json.dumps(decode(repo, tree_id))

    orig_size = int(info[2].split(b' ')[1].strip())
    curr_size = len(data)
    if orig_size != curr_size:
        warnings.warn('Source size has changed from {0} to {1}.'.format(
            orig_size, curr_size))

    click.echo(data)


@cli.command()
@click.option('--source', type=click.File('rb'), default='-')
@click.option('--git', type=click.Path(exists=True), default='.')
def clean(source, git):
    """Store a JSON file in Git repository."""
    repo = Repo(git)
    data = json.load(source)
    index = encode(
        repo,
        data,
    )
    click.echo("version https://github.com/jirikuncar/git-json-tree/v1\n"
               "oid sha1:{index}\n"
               "size {size}".format(
                   index=index.decode('ascii'), size=len(json.dumps(data))))
