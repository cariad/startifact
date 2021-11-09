CLI usage
=========

Staging to a bucket when you know the name
------------------------------------------

Pass the path to the artifact to stage, plus ``--bucket-name`` to specify the name of the S3 bucket to upload to.

.. code-block:: console

   $ startifact artifact.tar.gz --bucket-name MyStagingBucket
