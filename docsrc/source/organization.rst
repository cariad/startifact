Organisation configuration
==========================

Introduction
------------

Startifact is designed to be run within organisations with multiple CI/CD pipelines that stage, download or otherwise *use* versioned artifacts.

Rather than configure Startifact within each pipeline, Startifact reads from a shared organisation-level configuration in Systems Manager.

As long as your CI/CD pipelines all authenticate to the same Amazon Web Services account, they will read the same configuration.

Choosing where to host the configuration
----------------------------------------

By default, Startifact reads and writes configuration to a Systems Manager parameter named ``/Startifact`` in your default account and region.

To change that parameter name, set an environment variable named ``STARTIFACT_PARAMETER``.

Performing or updating the organisation setup
---------------------------------------------

Volunteer a :ref:`privileged <IAM policies>` human being to run:

.. code-block:: console

   startifact --setup

They will be asked to:

1. Confirm the configuration parameter name, region and account.
2. Enter the name of the Systems Manager parameter holding the bucket's name.
3. Enter the name of the region that hosts the Systems Manager parameter that holds the bucket's name.
4. Enter the name of the region that hosts the bucket.
5. Optionally enter a bucket key prefix.
6. Enter the name of the region where artifacts should be recorded in Systems Manager.
7. Optionally enter a name prefix for the Systems Manager parameters that record artifact versions. Without a prefix, versions will be recorded as `/{project}/Latest`.
8. Confirm the configuration parameter name, region and account one last time before committing.
