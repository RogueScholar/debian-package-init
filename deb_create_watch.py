#!/usr/bin/env python2

from argparse import ArgumentParser
import re

# debian/watch templates based on https://wiki.debian.org/debian/watch

watch_templates = {
    'github.com/(?P<user>[\w\-]*)/(?P<project>[\w\-]*)': """
opts=filenamemangle=s/.+\/v?(\d\S*)\.tar\.gz/{pkgname}-$1\.tar\.gz/ \\
  https://{url}/tags .*/v?(\d\S*)\.tar\.gz
""",

    'metacpan.org': """
https://metacpan.org/release/{project} .*/{project}-v?(\d[\d.]+)\.(?:tar(?:\.gz|\.bz2)?|tgz|zip)$
""",

    'pypi.python.org/pypi/(?P<project>[\w\-]*)': """
https://pypi.python.org/packages/source/{project_first_letter}/{project}/{project}-(\d\S*)\.tar\.gz
""",

    'code.google.com/p/(?P<project>[\w\-]*)': """
http://code.google.com/p/{project}/downloads/list?can=1 .*/{project}-(\d\S*)\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))
""",

    'bitbucket.org/(?P<user>[\w\-]*)/(?P<project>[\w\-]*)': """
https://bitbucket.org/{user}/{project}/downloads .*/(\d\S*)\.tar\.gz
""",

    'search.cpan.org': """
http://search.cpan.org/dist/{project}/   .*/{project}-v?(\d[\d.-]+)\.(?:tar(?:\.gz|\.bz2)?|tgz|zip)$
""",

    'launchpad.net/(?P<project>[\w\-]*)': """
https://launchpad.net/{project}/+download .*/{project}-(.*).tar.gz
""",

    'codingteam.net/project/(?P<project>[\w\-]*)': """
https://codingteam.net/project/{project}/download project/{project}/download/file/{project}-(\d\S*).tar.gz
    """
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
    watch = watch_tpl.format(**d)
    watch = "version=3\n%s" % watch

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
