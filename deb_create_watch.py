#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# deb_create_watch.py: generates a debian/watch file from a project's VCS URL
# Copyright (C) 2015 Federico Ceratto
#           (C) 2020 Peter J. Mello <admin@petermello.net>.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser
import logging
import re

log = logging.getLogger(__name__)

# The following templates are based on <https://wiki.debian.org/debian/watch>
# and <https://wiki.debian.org/Python/LibraryStyleGuide>

watch_templates = {
    'github.com/(?P<user>[\w\-]*)/(?P<project>[\w\-]*)': """
opts=filenamemangle=s/.+\/v?(\d\S+)\.tar\.gz/{pkgname}-$1\.tar\.gz/ \\
  https://{url}/tags .*/v?(\d\S+)\.tar\.gz
""",

    'pypi.python.org/pypi/(?P<project>[\w\.\-]*)': """
opts="uversionmangle=s/(\d)[_\.\-\+]?((RC|rc|pre|dev|beta|alpha)\d+)$/$1~$2/,\\
  pgpsigurlmangle=s/$/.asc/" \\
  https://pypi.debian.net/{project}/{project}-(.+)\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))
""",

    'gitlab.com/(?P<user>[\w\-]*)/(?P<project>[\w\-]*)': """
opts=filenamemangle=s/.*\/archive\/(\d\S+)\/{project}.*\.tar\.gz/{project}-$1\.tar\.gz/g \\
  https://gitlab.com/{user}/{project}/tags?sort=updated_desc \\
  .*/archive/(\d\S+)/.*\.tar\.gz.*
""",

    'bitbucket.org/(?P<user>[\w\-]*)/(?P<project>[\w\-]*)': """
https://bitbucket.org/{user}/{project}/downloads?tab=tags \\
  .*/v?(\d\S+)\.tar\.gz
""",

    'metacpan.org': """
https://metacpan.org/release/{project} .*/{project}-v?(\d[\d.]+)\.(?:tar(?:\.gz|\.bz2)?|tgz|zip)$
""",

    'search.cpan.org': """
https://search.cpan.org/dist/{project}/ \\
  .*/{project}-v?(\d[\d.-]+)\.(?:tar(?:\.gz|\.bz2)?|tgz|zip)$
""",

    'launchpad.net/(?P<project>[\w\-]*)': """
opts=pgpsigurlmangle=s/$/.asc/ https://launchpad.net/{project}/ \\
  https://launchpad.net/.*download/{project}-([.\d]+)\.(?:tar\.(?:gz|bz2|xz))
""",

    'code.google.com/p/(?P<project>[\w\-]*)': """
https://code.google.com/p/{project}/downloads/list?can=1 \\
  .*/{project}-(\d\S+)\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))
""",

    'codingteam.net/project/(?P<project>[\w\-]*)': """
https://codingteam.net/project/{project}/download \\
  project/{project}/download/file/{project}-v?(\d\S+)\.tar\.gz
""",
}


def detect_hosting_service(url, pkg_name=None):
    """Detect well-known hosting service

    :param url: project URL
    :param pkg_name: optional package name
    :returns: proposed project name (str), watch file contents (str)
    """

    if not url.startswith(('http://', 'https://')):
        raise Exception("Unknown protocol in URL")

    url = url.rstrip('/')
    url = url.split('/', 2)[-1]  # remove http[s]://

    for url_re in sorted(watch_templates):
        match = re.match(url_re, url)
        if match:
            break

    if not match:
        raise Exception("Unknown service")

    watch_tpl = watch_templates[url_re]

    d = match.groupdict()
    d['url'] = url
    d['project_first_letter'] = d['project'][0]
    d['pkgname'] = pkg_name or d['project'].lower()

    proposed_project_name = url.split('/')[-1]
    log.debug("Package name: %s", d['pkgname'])
    log.debug("Project full name: %s", proposed_project_name)
    log.debug("Project name: %s", proposed_project_name)
    watch = watch_tpl.format(**d)
    watch = "version=4%s" % watch

    return proposed_project_name, watch


def write_watch_file(contents):
    with open('debian/watch', 'w') as f:
        f.write(contents)


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--pkg-name')
    return ap.parse_args()


def main():
    args = parse_args()
    proposed_project_name, watch = detect_hosting_service(args.url,
                                                          args.pkg_name)
    write_watch_file(watch)


if __name__ == '__main__':
    main()
