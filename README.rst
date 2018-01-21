Git-JSON-Tree
=============

Encode and decode JSON files as directory structure in Git.

Installation
------------

Clone this repository and run pip:

.. code-block:: console

   $ pip install -e .

Move to a repository where you would like to filter JSON files and
add following lines to files:

``.git/config``

.. code-block::

   [filter "git-json-tree"]
       smudge = "git-json-tree smudge"
       clean = "git-json-tree clean"
       required

``.gitattributes``

.. code-block::

   \*.json  filter=git-json-tree


Pointer file format
-------------------

Git Git-JSON-Tree's pointer file looks like this:

.. code-block::

   version https://raw.githubusercontent.com/jirikuncar/git-json-tree/v1/spec
   oid sha1:2f769492d6b634b86b82e916630da8a693e9c20e
   size 12345

It tracks the version of Git DirJSON you're using, followed by a unique identifier
for the JSON file (oid). It also stores the size of the target JSON file.
