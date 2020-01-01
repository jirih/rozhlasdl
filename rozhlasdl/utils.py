import os
import re
from os.path import join
from urllib.parse import urlparse, urlunparse

rozhlas_regex = re.compile(
    r'https://'
    r'((?P<subdomain>\w+)\.)?'
    r'rozhlas.cz/.*', re.IGNORECASE)


def str_to_win_file_compatible(s):
    s = s.strip()
    s = s.replace("\\", ";")
    s = re.sub(r"[/|]", ";", s)
    s = re.sub(r":", "-", s)
    s = re.sub(r"[{\[]", "(", s)
    s = re.sub(r"[}\]]", ")", s)
    s = re.sub(r"\"", "'", s)
    s = re.sub(r"[<>*?]", "", s)
    s = re.sub(r"\s+", ' ', s)
    return s


def complete_url(url, url_base):
    parsed_url = urlparse(url)
    if parsed_url.scheme == "":
        parsed_url_base = urlparse(url_base)
        return urlunparse((parsed_url_base.scheme, parsed_url_base.netloc, parsed_url.path, parsed_url.params,
                           parsed_url.query, parsed_url.fragment))
    else:
        return url


def add_folder_from_subdomain(url, folder):
    m = rozhlas_regex.search(url)
    subdomain = m.group('subdomain')
    if subdomain is not None:
        folder = join(folder, subdomain.lower())
    return folder


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
