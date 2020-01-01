import contextlib
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen, urlretrieve

from RozhlasException import RozhlasException


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
    with contextlib.closing(urlopen(Request(url, method='HEAD'))) as head_resp:
        content_length = int(head_resp.info()["Content-Length"])
    return content_length


class FileDownloader:
    def __init__(self, folder=str(Path.home()), progress_bar=None, no_duplicates=True):
        self.progress_bar = progress_bar
        self.no_duplicates = no_duplicates
        if os.path.isdir(folder):
            self.folder = folder
        else:
            raise RozhlasException("Folder %s does not exist" % folder)

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
                    print("File %s already exists but has different length. New version will be downloaded." % path)
                    path = add_index_to_path(path, 1)
                else:
                    print("File %s already exists. Skipping." % path)
                    return
            else:
                path = add_index_to_path(path, 1)

        print("Downloading %s" % path)
        urlretrieve(url, path, self.progress_bar)
