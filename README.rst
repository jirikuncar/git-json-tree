DirSON
======

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

   [filter "dirson"]
       smudge = "dirson smudge"
       clean = "dirson clean"
       required

``.gitattributes``

.. code-block::

   \*.json  filter=dirson


Pointer file format
-------------------

Git DirSON's pointer file looks like this:

.. code-block::

   version https://raw.githubusercontent.com/jirikuncar/dirson/v1/spec
   oid sha1:2f769492d6b634b86b82e916630da8a693e9c20e
   size 12345

It tracks the version of Git DirJSON you're using, followed by a unique identifier
for the JSON file (oid). It also stores the size of the target JSON file.
