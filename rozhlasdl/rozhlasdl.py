# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from os.path import isabs
from os.path import join
from pathlib import Path

from log.LoggerFactory import LoggerFactory
from utils import makedirs, rozhlas_regex


def validate_url(url):
    return rozhlas_regex.match(url) is not None


def create_parser():
    parser = argparse.ArgumentParser(description='Download mp3 from rozhlas.cz urls')
    parser.add_argument('url', nargs='+', help='<Required> URLs', action='store')
    parser.add_argument('-d', '--dir', help='Directory for saving downloaded files',
                        default=join(str(Path.home()), "Downloads"), dest='dir', action='store')
    parser.add_argument('-n', '--no-duplicate-skipping', help='Duplicates are not skipped',
                        dest="no_duplicate_skipping", default=False, action='store_true')
    parser.add_argument('-f', '--follow-next-pages', help='Follow next pages',
                        dest="follow_next_pages", default=False, action='store_true')
    parser.add_argument('-m', '--max-next-pages', help='Maximal number of next pages to follow',
                        dest="max_next_pages", default=3, action='store')
    parser.add_argument('-s', '--simulate-audio-download', help='Downloads of audio files will be faked',
                        dest="fake_download", default=False, action='store_true')
    parser.add_argument('-u', '--utf-8',
                        help='Explicitly set UTF-8 for stdin, stdout, stderr - against problems when piping',
                        dest="utf8", default=False, action='store_true')
    parser.add_argument('-p', '--progress-bar-disabled', help='Disable progress-bar',
                        dest="progress_bar_enabled", default=True, action='store_false')
    parser.add_argument('-l', '--log-file', help='Log file',
                        dest="log_file", default=None, action='store')
    parser.add_argument('-t', '--use-page-title', help='Use page title instead of audio description',
                        dest="use_page_title", action='store_true', default=False)
    parser.add_argument('-v', '--verbose', help='Verbose',
                        dest="verbose", action='count', default=0)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.utf8:
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='surrogateescape')
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='backslashescape')
        sys.stdin = open(sys.stdin.fileno(), 'r', encoding='utf-8', errors='surrogateescape')
    urls = args.url
    folder = args.dir
    no_duplicates = not args.no_duplicate_skipping
    follow_next_pages = args.follow_next_pages
    fake_download = args.fake_download
    max_next_pages = int(args.max_next_pages)
    progress_bar_enabled = args.progress_bar_enabled
    log_file = args.log_file
    verbose = args.verbose
    use_page_title = args.use_page_title

    if not isabs(folder):
        folder = join(str(Path.home()), "Downloads", folder)
    makedirs(folder)

    logger = get_logger(get_log_file(folder, log_file), get_log_level(verbose))

    from MainDownloader import MainDownloader  # if imported earlier, loggers will not be created correctly
    main_downloader = MainDownloader(folder, no_duplicates=no_duplicates, follow_next_pages=follow_next_pages,
                                     fake_download=fake_download, max_next_pages=max_next_pages,
                                     progress_bar_enabled=progress_bar_enabled, use_page_title=use_page_title)

    logger.debug("Download started.")

    for url in urls:
        if validate_url(url):
            # noinspection PyBroadException
            try:
                main_downloader.download_url(url)
            except Exception as ex:
                logger.exception("Exception %s raised when processing %s ." % (str(ex), url))
        else:
            logger.error("%s is not a valid url." % url)

    logger.debug("Download finished.")


def get_log_file(folder, log_file):
    if log_file is None:
        return None
    if not isabs(log_file):
        log_file = join(folder, log_file)
    return log_file


def get_logger(log_file, log_level):
    LoggerFactory.set(log_file=log_file, default_log_level=log_level)
    return LoggerFactory.get("rozhlasdl")


def get_log_level(verbose):
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    return log_level


if __name__ == "__main__":
    main()
