Organisation configuration
==========================

Introduction
------------

Startifact is designed to be run within organisations with multiple CI/CD pipelines.

Rather than configure Startifact within each pipeline, Startifact reads from a shared organisation-level configuration in Systems Manager.

As long as your CI/CD pipelines all authenticate to the same Amazon Web Services account, they will read the same configuration.

Choosing where to host the configuration
----------------------------------------

By default, Startifact reads and writes configuration to a Systems Manager parameter named ``/startifact``.

To change that parameter name, set an environment variable named ``STARTIFACT_PARAMETER``. Take care, however, that you set that variable on *every* machine that Startifact runs on.

Performing or updating the organisation setup
---------------------------------------------

Volunteer a :ref:`privileged <Regional IAM policies>` human being to run:

.. code-block:: console

   startifact --setup

They will be asked to:

1. Enter the **comma-separated list of regions** that have :ref:`been prepared <Amazon Web Services>`. For example, ``us-west-2,us-east-1,eu-west-1``.
2. Enter the **name of the Systems Manager parameter that holds the artifact bucket's name**.
3. **Optionally enter a key prefix for the artifacts bucket.** If a prefix is set, it must contain only alphanumeric, ``-``, ``_`` or ``.`` characters, and must end with a ``/``. For example, ``my-platform/``.
4. **Optionally enter a name prefix for the projects recorded in Systems Manager Parameter Store.** If a prefix is set, it must start with a ``/`` and not end with a ``/``. For example, ``/my-platform``.
5. **Confirm the values before committing.**
