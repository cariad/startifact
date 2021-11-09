CLI usage
=========

The first three arguments on the command line must be:

#. Name
#. Path
#. Version

For example:

.. code-block:: console

   $ startifact MyServerlessFunction dist.tar.gz 1.0.0


The remaining arguments depend on your particular situation.

Staging to a bucket when you know the name
------------------------------------------

Set ``--bucket-name`` to specify the name of the S3 bucket to upload to.

.. code-block:: console

   $ startifact MyServerlessFunction dist.tar.gz 1.0.0 --bucket-name MyStagingBucket
