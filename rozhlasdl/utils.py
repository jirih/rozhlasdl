# -*- coding: utf-8 -*-
import os
import re
from os.path import join
from urllib.parse import urlparse, urlunparse, quote

rozhlas_regex = re.compile(
    r'https://'
    r'((?P<subdomain>\w+)\.)?'
    r'rozhlas.cz/.*', re.IGNORECASE)


def str_to_win_file_compatible(s):
    if s is None:
        return "None"
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


def get_subdomain(url):
    m = rozhlas_regex.search(url)
    return m.group('subdomain')


def safe_path_join(path, folder):
    if folder is not None:
        path = join(path, folder)
    return path


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def find_elements_with_attribute_containing(root, tag, attribute, content):
    result = []
    if attribute in root.attrib:
        if content in root.attrib[attribute]:
            result.append(root)

    elements = root.findall(".//%s[@%s]" % (tag, attribute))
    elements = filter(lambda x: content in x.attrib[attribute], elements)
    result.extend(elements)
    return result


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(quote(s))