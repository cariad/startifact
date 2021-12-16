CLI usage
=========

Staging an artifact via the CLI
-------------------------------

To stage an artifact, pass the project name, version and ``--stage`` argument with the path to the file:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --stage dist.tar.gz

To attach metadata to the artifact, include any number of ``--metadata`` arguments. Each value must be a ``key=value`` pair. If the value contains multiple ``=`` characters then a pair will be made by splitting on the first.

.. code-block:: console

   $ startifact SugarWater 1.0.9000 \
       --stage    dist.tar.gz \
       --metadata lang=dotnet \
       --metadata hash=9876=

To perform a dry run, swap ``--stage`` for ``--dry-run``:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --dry-run dist.tar.gz

Getting artifact information via the CLI
----------------------------------------

To get information about a staged artifact, pass the project name, version and ``--info``:

.. code-block:: console

   $ startifact SugarWater 1.0.1 --get

The version can be omitted or ``latest`` to infer the latest version.

.. code-block:: console

   $ startifact SugarWater --get

Downloading an artifact via the CLI
-----------------------------------

To download an artifact, pass the project name, version and ``--download`` argument with the path to download to:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --download download.tar.gz

The version can be omitted or ``latest`` to infer the latest version.
