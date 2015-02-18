Helper scripts to create new Debian packages
--------------------------------------------

debpin.py
----------

Fetch the source .tar.gz file, create the packaging repository and populate the packaging directory with debdry.

Requirements:
    apt-get install debdry git debhelper

Usage:
    debpin.py <upstream repository URL>

Examples:
    debpin.py https://github.com/svinota/pyroute2  # Create a Python package from a GitHub repository

See the help (-h) for details.

deb_create_watch.py
-------------------

Create a debian/watch file from a project URL using a set of popular hosting services.


