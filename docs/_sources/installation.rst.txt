Installation
============

Requirements
------------

- Python 3.8 or later.
- An Amazon Web Services account.

Installing
----------

The command line application and Python package are both installed via pip:

.. code-block:: console

   pip install startifact

You **must** set an environment variable named ``STARTIFACT_REGIONS`` to describe the :ref:`prepared regions <Amazon Web Services>` that Startifact can use.

Comma-separate each region without spaces. For example:

.. code-block:: console

   STARTIFACT_REGIONS="us-east-1,us-west-2,eu-west-2"

Your Amazon Web Services account
--------------------------------

Startifact will **not** deploy any IAM policies or S3 buckets to your Amazon Web Services account for you. You must :ref:`deploy your own cloud resources <Amazon Web Services>`.
