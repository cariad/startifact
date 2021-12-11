CLI usage
=========

Staging an artifact via the CLI
-------------------------------

To stage an artifact, pass the project name, version and ``--stage`` argument with the path to the file:

.. code-block:: console

   startifact SugarWater 1.0.9000 --stage dist.tar.gz

Where the version number comes from depends on your CI/CD setup. For example, I use CircleCI and I stage artifacts on tags, so I know I can pull the version number from the ``CIRCLE_TAG`` environment variable:

.. code-block:: console

   startifact SugarWater "${CIRCLE_TAG}" --stage dist.tar.gz

To attach metadata to the artifact, include any number of ``--metadata`` arguments. Each value must be a ``key=value`` pair. If the value contains multiple `=` characters then a pair will be made by splitting on the first.

.. code-block:: console

   startifact SugarWater 1.0.9000 --stage dist.tar.gz --metadata lang=dotnet --metadata hash=9876=

To perform a dry run, swap ``--stage`` for ``--dry-run``:

.. code-block:: console

   startifact SugarWater 1.0.9000 --dry-run dist.tar.gz

Getting the latest artifact version via the CLI
-----------------------------------------------

To get the version number of the latest artifact staged for a project, pass the project name and ``--get`` argument for ``version``:

.. code-block:: console

   startifact SugarWater --get version

The version number will be emitted to ``stdout``.

Downloading an artifact via the CLI
-----------------------------------

To download an artifact, pass the project name, *optionally* the version number, and the ``--download`` argument with the path to download to:

.. code-block:: console

   startifact SugarWater 1.0.9000 --download download.tar.gz

If the version is omitted or ``latest`` then the latest artifact will be downloaded, otherwise the literal version will be downloaded.
