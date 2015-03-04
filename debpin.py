#!/usr/bin/env python2

from argparse import ArgumentParser
import logging
import os
import subprocess

from deb_create_watch import detect_hosting_service, write_watch_file

log = logging.getLogger('debpin')


def setup_logging(debug):
    lvl = logging.DEBUG if debug else logging.INFO
    log.setLevel(lvl)
    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('url', help="Repository URL")
    ap.add_argument('--pkg-name', help="Debian source package name")
    ap.add_argument('-d', '--debug', action="store_true", help="Debug mode")
    return ap.parse_args()


def run_cmd(*a):
    log.debug('$ %s', ' '.join(a))
    subprocess.check_call(list(a))


def create_git_repo(pkgname):
    os.mkdir(pkgname)
    os.chdir(pkgname)
    run_cmd('git', 'init', '.')


def main():
    args = parse_args()
    setup_logging(args.debug)

    proposed_project_name, watch = detect_hosting_service(
        args.url, pkg_name=args.pkg_name)

    if not args.pkg_name:
        args.pkg_name = proposed_project_name

    log.info("Creating Git repository")
    create_git_repo(args.pkg_name)

    log.debug("Creating debian directory")
    os.mkdir('debian')

    log.info("Generating watch file")
    write_watch_file(watch)
    if args.debug:
        log.debug('-' * 10)
        with open('debian/watch') as f:
            for line in f:
                log.debug(line.rstrip())

        log.debug('-' * 10)

    log.debug("Generating temporary changelog file")
    run_cmd('/usr/bin/dch', '--create', "--package", args.pkg_name, '--empty',
            '-v', '0.0.0-1')

    if args.debug:
        log.debug("Running uscan test")
        run_cmd('/usr/bin/uscan', '--report')

    log.info("Importing tarball using uscan")
    run_cmd('/usr/bin/git', 'import-orig', '--uscan', '-v', '--no-interactive')

    log.debug("Deleting temporary changelog")
    os.unlink('debian/changelog')

    log.info("Running debdry")
    run_cmd('/usr/bin/debdry', '-v')

    log.debug("Adding debian directory to Git")
    run_cmd('/usr/bin/git', 'add', 'debian')


if __name__ == '__main__':
    main()
