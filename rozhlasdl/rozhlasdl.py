import argparse
import traceback
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
    return parser


def main():
    parser = create_parser()
    urls = parser.parse_args().url
    folder = parser.parse_args().dir
    no_duplicates = not parser.parse_args().no_duplicate_skipping

    if not isabs(folder):
        folder = join(str(Path.home()), "Downloads", folder)
    makedirs(folder)

    main_downloader = MainDownloader(folder, no_duplicates=no_duplicates)
    for url in urls:
        if validate_url(url):
            # noinspection PyBroadException
            try:
                main_downloader.download_url(url)
            except Exception as ex:
                traceback.print_exc()
        else:
            print("%s is not a valid url" % url)


if __name__ == "__main__":
    main()
