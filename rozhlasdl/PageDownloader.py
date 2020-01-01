import urllib.request


class PageDownloader():
    def __init__(self, page_url):
        self.page_url = page_url

    def download(self):
        req = urllib.request.Request(self.page_url)
        with urllib.request.urlopen(req) as response:
            charset = response.info().get_content_charset() or "utf-8"
            the_page = response.read().decode(charset)
        return the_page
