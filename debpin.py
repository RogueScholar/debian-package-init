#!/usr/bin/env python2

from argparse import ArgumentParser
import os
import subprocess

from deb_create_watch import detect_hosting_service, write_file


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--pkg-name')
    return ap.parse_args()


def run_cmd(*a):
    print '$', ' '.join(a)
    subprocess.check_call(list(a))


def create_git_repo(pkgname):
    os.mkdir(pkgname)
    os.chdir(pkgname)
    run_cmd('git', 'init', '.')


def main():
    args = parse_args()

    proposed_project_name, watch = detect_hosting_service(args.url)

    if not args.pkg_name:
        args.pkg_name = proposed_project_name

    create_git_repo(args.pkg_name)
    os.mkdir('debian')
    write_file('debian/watch', watch)
    run_cmd('/usr/bin/dch', '--create', "--package", args.pkg_name, '--empty', '-v', '0.0.0-1')
    run_cmd('/usr/bin/git', 'import-orig', '--uscan', '-v', '--no-interactive')
    os.unlink('debian/changelog')
    run_cmd('/usr/bin/debdry')
    run_cmd('/usr/bin/git', 'add', 'debian')


if __name__ == '__main__':
    main()
