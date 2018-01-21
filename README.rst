===============
 Git-JSON-Tree
===============

.. image:: https://img.shields.io/travis/jirikuncar/git-json-tree.svg
   :target: https://travis-ci.org/jirikuncar/git-json-tree

.. image:: https://img.shields.io/coveralls/jirikuncar/git-json-tree.svg
   :target: https://coveralls.io/r/jirikuncar/git-json-tree

.. image:: https://img.shields.io/github/tag/jirikuncar/git-json-tree.svg
   :target: https://github.com/jirikuncar/git-json-tree/releases

.. image:: http://readthedocs.org/projects/git-json-tree/badge/?version=latest
   :target: http://git-json-tree.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/github/license/jirikuncar/git-json-tree.svg
   :target: https://github.com/jirikuncar/git-json-tree/blob/master/LICENSE

Encode and decode JSON files as Git tree objects.

**This is an experimental developer preview release.**

Installation
------------

The latest release is available on PyPI and can be installed using
``pip``:

::

    $ pip install git-json-tree

The development version can be installed directly from the Git repository:

::

    $ pip install -e git+https://github.com/jirikuncar/git-json-tree.git#egg=git-json-tree


Integration with Git
--------------------

Move to a repository where you would like to store JSON files and
add following lines to files:

``.git/config``

.. code-block:: ini

   [filter "git-json-tree"]
       smudge = "git-json-tree smudge"
       clean = "git-json-tree clean"
       required  # optional

``.gitattributes``

.. code-block:: text

   *.json  filter=git-json-tree


Pointer file format
~~~~~~~~~~~~~~~~~~~

Git Git-JSON-Tree's pointer file looks like this:

.. code-block:: text

   version https://github.com/jirikuncar/git-json-tree/tree/v1
   oid sha1:2f769492d6b634b86b82e916630da8a693e9c20e
   size 12345

It tracks the version of Git-JSON-Tree you're using, followed by a unique
identifier for the JSON file (oid). It also stores the size of the target JSON
file.

**NOTE**:
   ``size`` is calculated from the encoded JSON string and it might differ
   depending on the version of serializer.


Use the command line
--------------------

Interaction with the storage can also take place via the command-line
interface (CLI).

First, you need to make sure that you are in a Git repository or you
know its location. The example shows a case when you are in the directory
with a Git repository.

.. code-block:: console

   $ echo '{"hello": "world", "version": 1}' | git-json-tree encode
   7123db01ad8c75a8df3508305bd891317ea36feb

Following the above example you can create a first commit of your JSON object.

.. code-block:: console

   $ export FIRST=$(git commit-tree 7123db01 -m First)

It is quite impractical to remember tree or commit sha1, hence we can give it
a reference name. The next steps uses the name ``master``, but you can decide
to use your own naming convention for tracking versions of your objects. Each
file can have its own branch or just a single tag.

.. code-block:: console

   $ git update-ref refs/heads/master $FIRST  # for new object

Storing a new version is very simple too.

.. code-block:: console

   $ export PARENT=$(git show-ref --hash refs/heads/master)
   $ echo '{"hello": "world", "version": 2}' | git-json-tree encode
   6f36c4272e88b14ab5e25a5419599534504c70fc
   $ export SECOND=$(git commit-tree 6f36c4272e -m Second -p $PARENT)
   $ git update-ref refs/heads/master $SECOND

Finally, you can retrive and decode a tree or commit.

.. code-block:: console

   $ git-json-tree decode  # HEAD
   $ git-json-tree decode $FIRST  # commit
   $ git-json-tree decode 7123db01  # tree id
