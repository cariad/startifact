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

Getting the latest artifact version via Python
----------------------------------------------

.. code-block:: python

    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater")

    print(artifact.version)

Downloading an artifact via Python
----------------------------------

.. code-block:: python

    from startifact import Session

    session = Session()

    artifact = session.get("SugarWater", "1.0.9000")

    artifact.downloader.download("download.tar.gz")

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
