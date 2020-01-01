import html5lib


class WebPageParser():
    def __init__(self, webpage_source):
        self.web_page = html5lib.parse(webpage_source)

    def get_root(self):
        return self.web_page
