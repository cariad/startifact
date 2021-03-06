Startifact
==========

**Startifact** is a command line application and Python package for staging and retrieving versioned artifacts in Amazon Web Services.

Features
--------

* Configuration is held in Amazon Web Services Systems Manager. Startifact operates consistently across all your CI/CD jobs by default.

* Optional metadata can be attached to artifacts at the point of staging then interrogated later.

* Configuration, artifacts and metadata are stored across as many regions as you care to provide. Startifact is :ref:`resilient to outages <Resilience>`.

Terms
-----

Say you have a CI/CD build job for a software component named "SugarWater". This build job produces:

* A "dist.tar.gz" file

* A hash of "dist.tar.gz"

* A semantic version number

In Startifact:

* "SugarWater" is a **project**.

* The "dist.tar.gz" file and the semantic version together are an **artifact**.

* The hash is recorded as **metadata**

Getting started
---------------

1. Prepare your :ref:`Amazon Web Services` account.
2. :ref:`Install <Installation>` Startifact.
3. Deploy your :ref:`organisation configuration <Organisation configuration>`.
4. Start :ref:`staging your artifacts <CLI usage>`.

Licence
-------

Startifact is released at `github.com/cariad/startifact <https://github.com/cariad/startifact>`_ under the MIT Licence.

See `LICENSE <https://github.com/cariad/startifact/blob/main/LICENSE>`_ for more information.

Contributing
------------

To contribute a bug report, enhancement or feature request, please raise an issue at `github.com/cariad/startifact/issues <https://github.com/cariad/startifact/issues>`_.

If you want to contribute a code change, please raise an issue first so we can chat about the direction you want to take.

Author
------

Hello! 👋 I'm **Cariad Eccleston** and I'm a freelance DevOps and backend engineer. My contact details are available on my personal wiki at `cariad.earth <https://cariad.earth>`_.

Please consider supporting my open source projects by `sponsoring me on GitHub <https://github.com/sponsors/cariad/>`_.

Acknowledgements
----------------

- Interactive configuration by `Asking <https://github.com/cariad/asking/>`_.
- CLI orchestration by `Cline <https://github.com/cariad/cline/>`_.
- Command line colours and styling by `Ansiscape <https://github.com/cariad/ansiscape/>`_.

Contents
--------

.. toctree::
   :maxdepth: 2

   self
   installation
   resilience
   aws
   organization
   cli
   python/index
   use-cases
