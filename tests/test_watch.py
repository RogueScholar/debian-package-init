import pytest

from deb_create_watch  import detect_hosting_service

urls_and_expected_watch = [
    ('https://code.google.com/p/ntplib/',
     'http://code.google.com/p/ntplib/downloads/list?can=1 .*/ntplib-(\d\S*)\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))'),
    ('https://pypi.python.org/pypi/geoip-lastlog/',
     """https://pypi.python.org/packages/source/g/geoip-lastlog/geoip-lastlog-(\d\S*)\.tar\.gz"""),
    ('https://code.google.com/p/ntplib/',
     'http://code.google.com/p/ntplib/downloads/list?can=1 .*/ntplib-(\d\S*)\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))'),
    ('https://bitbucket.org/regebro/pyroma',
     """https://bitbucket.org/regebro/pyroma/downloads .*/(\d\S*)\.tar\.gz"""),
    ('http://launchpad.net/diodon/',
     'https://launchpad.net/diodon/+download .*/diodon-(.*).tar.gz'),
    ('http://github.com/defnull/bottle',
     """opts=filenamemangle=s/.+\/v?(\d\S*)\.tar\.gz/bottle-$1\.tar\.gz/ \\
  https://github.com/defnull/bottle/tags .*/v?(\d\S*)\.tar\.gz"""),

]


@pytest.fixture(params=urls_and_expected_watch)
def url_and_expected_watch(request):
    url, watch = request.param
    watch = "version=3\n\n%s\n" % watch
    return url, watch


def test_detect_hosting(url_and_expected_watch):
    url, expected_watch = url_and_expected_watch
    pkg_name, watch = detect_hosting_service(url)
    assert watch == expected_watch
