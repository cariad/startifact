Resilience
==========

Startifact is designed for pessimism and resilience by balancing between any number of Amazon Web Services regions that you grant access to.

Resilient configuration
-----------------------

Startifact records your :ref:`organisation configuration <Organisation configuration>` in all of your regions.

.. caution::

   If you ever push a change to your configuration and any regions are unavailable then your configuration will be globally inconsistent. Startifact will log a warning if this occurs.

   You should re-run the configuration as soon as those regions come back online so that any reads from those regions pull the latest, correct settings.

When your configuration needs to be read, Startifact shuffles your regions then interrogates them sequentially until one provides its configuration.

Resilient uploads
-----------------

Each artifact is uploaded to and recorded in all of your regions.

Resilient version interrogations
--------------------------------

When Startifact needs to look-up the latest version number of an artifact, it shuffles your regions then interrogates them sequentially until at least half have responded. The latest version claimed by these regions is taken as truth.

Resilient downloads
-------------------

When an artifact download is requested, Startifact shuffles your regions then attempts to use each sequentially until a download succeeds.

Resilient metadata
-------------------

When artifact metadata is requested, Startifact shuffles your regions then attempts to use each sequentially until a download succeeds.
