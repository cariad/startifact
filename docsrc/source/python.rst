Python usage
============

Staging an artifact via Python
------------------------------

.. code-block:: python

    from startifact import Session

    session = Session()
    session.stage("SugarWater", "1.0.9000", path="dist.tar.gz")

Metadata can be attached in the same call:

.. code-block:: python

    from startifact import Session

    session = Session()
    session.stage(
        "SugarWater",
        "1.0.9000",
        metadata={
            "lang": "dotnet",
            "hash": "9876=",
        },
        path="dist.tar.gz",
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
    artifact.download("download.tar.gz")

Reading and appending metadata
------------------------------

Metadata can be added to any artifact, but values cannot be removed or modified. History can't be changed.

.. code-block:: python

   from startifact import Session

   session = Session()
   artifact = session.get("SugarWater", "1.0.9000")

   language = artifact["lang"]

   artifact["deployed"] = "true"
   artifact.save_metadata()
