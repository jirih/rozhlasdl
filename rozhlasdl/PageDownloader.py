# -*- coding: utf-8 -*-
import contextlib
import urllib.request
from urllib.error import HTTPError

from retry import retry


class PageDownloader():
    def __init__(self, page_url):
        self.page_url = page_url

    def download(self):
        req = urllib.request.Request(self.page_url)
        with contextlib.closing(self.open_url(req)) as response:
            charset = response.info().get_content_charset() or "utf-8"
            the_page = response.read().decode(charset)
        return the_page

    @retry(HTTPError, tries=3, delay=5, backoff=2)
    def open_url(self, req):
        return urllib.request.urlopen(req)
