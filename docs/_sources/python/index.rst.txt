Python usage
============

Sessions
--------

The :class:`startifact.Session` class is the entry point to using Startifact in a Python script.

Each session maintains its own cache and should be reused as much as possible.

Each session can also be limited to a subset or a single region if required.

Staging an artifact via Python
------------------------------

.. code-block:: python

    from pathlib import Path
    from semver import VersionInfo
    from startifact import Session

    session = Session()

    session.stage(
        "SugarWater",
        VersionInfo(1, 0, 9000),
        path=Path("dist.tar.gz"),
    )

Metadata can be attached in the same call:

.. code-block:: python

    from pathlib import Path
    from semver import VersionInfo
    from startifact import Session

    session = Session()

    session.stage(
        "SugarWater",
        "1.0.9000",
        metadata={
            "lang": "dotnet",
            "hash": "9876=",
        },
        path=Path("dist.tar.gz"),
    )

.. warning::

   Metadata keys that start with ``startifact:`` are reserved for internal metadata.

By default, Startifact does not save an artifact's filename. Startifact assumes that the filename isn't meaningful, and so saves time and energy by ignoring it.

Sometimes, though -- like when staging a Python package wheel -- the filename is meaningful and should be saved.

To have Startifact save an artifact's filename, pass ``save_filename=True``:

.. code-block:: python

    from pathlib import Path
    from semver import VersionInfo
    from startifact import Session

    session = Session()

    session.stage(
        "SugarWater",
        VersionInfo(1, 0, 9000),
        path=Path("dist.tar.gz"),
        save_filename=True,
    )

You must also pass ``load_filename=True`` when downloading the artifact.

Getting the latest artifact version via Python
----------------------------------------------

To get the latest version number of a project, call :func:`startifact.Session.get` to get an artifact then interrogate the :attr:`startifact.Artifact.version` property.

.. code-block:: python

    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater")

    print(artifact.version)

Downloading an artifact via Python
----------------------------------

.. code-block:: python

    from pathlib import Path
    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater", "1.0.9000")

    artifact.downloader.download(Path("download.tar.gz"))

To restore the artifact's original filename, pass a directory and include the ``load_filename=True`` flag:

.. code-block:: python

    from pathlib import Path
    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater", "1.0.9000")

    artifact.downloader.download(Path("."), load_filename=True)

Reading metadata
----------------

.. code-block:: python

    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater", "1.0.9000")

    language = artifact["lang"]

    print(language)


Classes
--------

.. toctree::
   :maxdepth: 2

   session
   artifact
   configuration_loader
