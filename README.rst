Helper scripts to create new Debian packages
--------------------------------------------

debpin.py
----------

Fetch the source .tar.gz file, populate the packaging directory with debdry.

Requirements:
    apt-get install debdry git debhelper

Usage:
    debpin.py <upstream repository URL>

See the help (-h) for details.

deb_create_watch.py
-------------------

Create a debian/watch file from a project URL using a set of popular hosting services.


