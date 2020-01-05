# -*- coding: utf-8 -*-
import argparse
import sys
import traceback
from datetime import datetime
from os.path import isabs
from os.path import join
from pathlib import Path

from MainDownloader import MainDownloader
from utils import makedirs, rozhlas_regex


def validate_url(url):
    return rozhlas_regex.match(url) is not None


def create_parser():
    parser = argparse.ArgumentParser(description='Download mp3 from rozhlas.cz urls')
    parser.add_argument('url', nargs='+', help='<Required> URLs', action='store')
    parser.add_argument('-d', '--dir', help='Directory for saving downloaded files',
                        default=join(str(Path.home()), "Downloads"), action='store')
    parser.add_argument('-n', '--no-duplicate-skipping', help='Duplicates are not skipped',
                        dest="no_duplicate_skipping", default=False, action='store_true')
    parser.add_argument('-f', '--follow-next-pages', help='Follow next pages',
                        dest="follow_next_pages", default=False, action='store_true')
    parser.add_argument('-m', '--max-next-pages', help='Maximal number of next pages to follow',
                        dest="max_next_pages", default=3, action='store')
    parser.add_argument('-s', '--simulate-audio-download', help='Downloads of audio files will be faked',
                        dest="fake_download", default=False, action='store_true')
    return parser


def main():
    parser = create_parser()
    urls = parser.parse_args().url
    folder = parser.parse_args().dir
    no_duplicates = not parser.parse_args().no_duplicate_skipping
    follow_next_pages = parser.parse_args().follow_next_pages
    fake_download = parser.parse_args().fake_download
    max_next_pages = int(parser.parse_args().max_next_pages)

    if not isabs(folder):
        folder = join(str(Path.home()), "Downloads", folder)
    makedirs(folder)

    main_downloader = MainDownloader(folder, no_duplicates=no_duplicates, follow_next_pages=follow_next_pages,
                                     fake_download=fake_download, max_next_pages=max_next_pages)

    print("Download started: %s" % datetime.now())

    for url in urls:
        if validate_url(url):
            # noinspection PyBroadException
            try:
                main_downloader.download_url(url)
            except Exception as ex:
                traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
        else:
            print("%s is not a valid url" % url)

    print("Download finished: %s" % datetime.now())
    print()


if __name__ == "__main__":
    main()
