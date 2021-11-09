CLI usage
=========

Staging to a bucket when you know the name
------------------------------------------

Pass the path to the artifact, its version, and ``--bucket-name`` to specify the name of the S3 bucket to upload to.

.. code-block:: console

   $ startifact artifact.tar.gz 1.0.0 --bucket-name MyStagingBucket
