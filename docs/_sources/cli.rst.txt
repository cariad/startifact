CLI usage
=========

Staging an artifact via the CLI
-------------------------------

To stage an artifact, pass the project name, version and ``--stage`` argument with the path to the file:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --stage dist.tar.gz


To perform a dry run, swap ``--stage`` for ``--dry-run``:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --dry-run dist.tar.gz

To attach metadata to the artifact, include any number of ``--metadata`` arguments. Each value must be a ``key=value`` pair. If the value contains multiple ``=`` characters then a pair will be made by splitting on the first.

.. code-block:: console

   $ startifact SugarWater 1.0.9000 \
       --stage    dist.tar.gz \
       --metadata lang=dotnet \
       --metadata hash=9876=

.. warning::

   Metadata keys that start with ``startifact:`` are reserved for internal metadata.

By default, Startifact does not save an artifact's filename. Startifact assumes that the filename isn't meaningful, and so saves time and energy by ignoring it.

Sometimes, though -- like when staging a Python package wheel -- the filename is meaningful and should be saved.

To have Startifact save an artifact's filename, pass ``--filename``:

.. code-block:: console

   $ startifact SugarWaterPackage 1.0.9000 \
       --filename \
       --stage sugarwater-1.0.9000-py3-none-any.whl

You must also pass ``--filename`` when downloading the artifact.

Getting artifact information via the CLI
----------------------------------------

To get information about a staged artifact, pass the project name, version and ``--info``:

.. code-block:: console

   $ startifact SugarWater 1.0.1 --info

The version can be omitted or ``latest`` to infer the latest version.

Downloading an artifact via the CLI
-----------------------------------

To download an artifact, pass the project name, version and ``--download`` argument with the path to download to:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --download download.tar.gz

The version can be omitted or ``latest`` to infer the latest version.

To restore the artifact's original filename, set ``--download`` to a directory and include the ``--filename`` flag:

.. code-block:: console

   $ startifact SugarWater 1.0.9000 --filename --download .
