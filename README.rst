semver_range
============

Python package for `semantic versioning 2.0.0 <http://semver.org/spec/v2.0.0.html>`_
that mimics the node `semver package <https://docs.npmjs.com/misc/semver>`_.
The interface is designed to be more "pythonic" and does not match semver’s logic 100%.

.. image:: https://github.com/ushkarev/semver_range/workflows/Test%20semver_range/badge.svg

Usage
-----

Install using ``pip install semver_range``. Sample usage:

.. code-block:: pycon

    >>> from semver_range import Version, Range
    >>> version_range = Range('>=0.1.1 <0.3.0')
    >>> Version('0.2.2') in version_range
    True
    >>> version_range.highest_version(['0.1.1', '0.2.0', '0.3.0'])
    <Version "0.2.0">

Alternatives
------------

`semantic_version <https://pypi.python.org/pypi/semantic_version/>`_ is a great package which differs slightly
in its implementation of semantic versioning, for example when incrementing a minor version of a pre-release.
