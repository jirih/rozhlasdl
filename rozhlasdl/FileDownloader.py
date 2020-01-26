# -*- coding: utf-8 -*-
import contextlib
import os
from pathlib import Path
from urllib.error import HTTPError, ContentTooShortError
from urllib.parse import urlparse
from urllib.request import Request, urlopen, urlretrieve

from retry import retry

from log.LoggerFactory import LoggerFactory
from utils import makedirs

LOGGER = LoggerFactory.get(__name__)


def create_path_with_index(path, index):
    split = os.path.splitext(path)
    return split[0] + " (%d)" % index + split[1]


def add_index_to_path(path, index):
    indexed_path = create_path_with_index(path, index)
    if os.path.isfile(indexed_path):
        return add_index_to_path(path, index + 1)
    else:
        return indexed_path


def get_size_of_file_on_web(url):
    with contextlib.closing(open_url_head(url)) as head_resp:
        content_length = int(head_resp.info()["Content-Length"])
    return content_length


@retry(HTTPError, tries=3, delay=5, backoff=2)
def open_url_head(url):
    return urlopen(Request(url, method='HEAD'))


class FileDownloader:
    def __init__(self, folder=str(Path.home()), progress_bar=None, no_duplicates=True, fake_download=False):
        self.progress_bar = progress_bar
        self.no_duplicates = no_duplicates
        self.folder = folder
        self.fake_download = fake_download

        if not os.path.isdir(folder):
            LOGGER.warning("Path %s does not exist. Creating." % self.folder)
            makedirs(folder)

    def download(self, url, name=None):
        if name is None:
            a = urlparse(url)
            name = os.path.basename(a.path)
        path = os.path.join(self.folder, name)

        content_length = get_size_of_file_on_web(url)

        if os.path.isfile(path):
            if self.no_duplicates:
                existing_file_length = os.path.getsize(path)
                if content_length != existing_file_length:
                    LOGGER.warning(
                        "File %s already exists but has different length. New version will be downloaded." % path)
                    path = add_index_to_path(path, 1)
                else:
                    LOGGER.info("File %s already exists. Skipping." % path)
                    return
            else:
                path = add_index_to_path(path, 1)

        LOGGER.debug("Downloading %s from %s." % (path, url))
        if self.fake_download:
            if self.progress_bar is None:
                LOGGER.info("Download of %s from %s done." % (path, url))
            else:
                LOGGER.info("100% |########################################################################|")
        else:
            self.url_download(path, url)
            if self.progress_bar is None:
                LOGGER.info("Download of %s from %s done." % (path, url))

    @retry((HTTPError, ContentTooShortError), tries=3, delay=5, backoff=2)
    def url_download(self, path, url):
        urlretrieve(url, path, self.progress_bar)
